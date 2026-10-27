import random
from collections import Counter
from collections.abc import Callable

from content.items import ITEMS
from content.monsters import MONSTERS
from content.places import WEATHER
from content.rules import ABILITIES, SKILLS, skill_label
from core.class_features import FeatureUnavailable, use_feature
from core.combat_system import Encounter
from core.commands import COMBAT_VERBS, HELP, Command, parse
from core.inventory import find_item, use_item
from core.narrator import CheckRequest, Narrator, Scene
from core.persistence import SaveError, SaveStore
from core.presentation import character_sheet, inventory_lines
from core.quests import complete_matching, create_quest, objective_text, player_tier
from core.world_generator import generate_world
from models.character import Character
from models.monster import Monster
from models.npc import NPC
from models.quest import Quest
from models.world_state import Location, WorldState
from utils.dice import Dice
from utils.matching import find_match

TRAVEL_HOURS = 2
EXPLORE_HOURS = 1
REST_HOURS = 8
JOURNAL_CONTEXT = 8
AUTOSAVE = "autosave"


class GameManager:
    def __init__(
        self,
        player: Character,
        world: WorldState,
        narrator: Narrator,
        rng: random.Random,
        saves: SaveStore,
    ):
        self.player = player
        self.world = world
        self.narrator = narrator
        self.rng = rng
        self.dice = Dice(rng)
        self.saves = saves
        self.encounter: Encounter | None = None
        self.running = True
        self._handlers: dict[str, Callable[[Command], list[str]]] = {
            "help": self._help,
            "look": self._look,
            "go": self._go,
            "map": self._map,
            "explore": self._explore,
            "talk": self._talk,
            "attack": self._attack,
            "dodge": self._dodge,
            "flee": self._flee,
            "use": self._use,
            "ability": self._ability,
            "rest": self._rest,
            "shop": self._shop,
            "buy": self._buy,
            "inventory": lambda _: inventory_lines(self.player),
            "stats": lambda _: character_sheet(self.player),
            "quests": self._quests,
            "check": self._check,
            "roll": self._roll,
            "save": self._save,
            "load": self._load,
            "quit": self._quit,
            "do": self._do,
        }

    @classmethod
    def new_game(
        cls, player: Character, narrator: Narrator, rng: random.Random, saves: SaveStore
    ) -> "GameManager":
        return cls(player, generate_world(rng), narrator, rng, saves)

    @classmethod
    def from_save(
        cls, saves: SaveStore, name: str, narrator: Narrator, rng: random.Random
    ) -> "GameManager":
        player, world = saves.load(name)
        return cls(player, world, narrator, rng, saves)

    def opening(self) -> list[str]:
        location = self.world.location
        lines = [
            f"== {location.name} ==",
            self.narrator.describe_location(self._scene()),
            *self._surroundings(),
        ]
        giver = self._quest_giver()
        if giver and not self.world.active_quests and giver.location == location.id:
            lines += [f"{giver.name} the {giver.occupation} approaches you."]
            lines += self._offer_quest(giver)
        return lines + ["Type 'help' to see what you can do."]

    def handle(self, text: str) -> list[str]:
        command = parse(text)
        if not command.verb:
            return []
        if self.encounter and command.verb not in COMBAT_VERBS:
            return [
                "You are in the middle of a fight! "
                "Try: attack, dodge, flee, use <item>, ability."
            ]
        if not self.encounter and command.verb in {"attack", "dodge", "flee"}:
            return [
                "There is nothing to fight here. Try 'explore' to look for trouble."
            ]
        return self._handlers[command.verb](command)

    def _help(self, _: Command) -> list[str]:
        width = max(len(usage) for usage, _ in HELP)
        return ["Commands:"] + [
            f"  {usage.ljust(width)}  {description}" for usage, description in HELP
        ]

    def _look(self, command: Command) -> list[str]:
        if self.encounter:
            return self.encounter.status()
        if command.args:
            return self._do(command)
        world = self.world
        return [
            f"== {world.location.name} ==",
            world.location.description,
            f"Day {world.day}, {world.time_of_day}. Weather: {world.weather}.",
            *self._surroundings(),
        ]

    def _surroundings(self) -> list[str]:
        people = ", ".join(
            f"{npc.name} the {npc.occupation}"
            for npc in self.world.npcs_at(self.world.current_location)
        )
        exits = ", ".join(location.name for location in self.world.neighbors())
        return [f"People here: {people or 'nobody'}.", f"Paths lead to: {exits}."]

    def _go(self, command: Command) -> list[str]:
        exits = ", ".join(location.name for location in self.world.neighbors())
        if not command.args:
            return [f"Where to? Paths lead to: {exits}."]
        destination = self.world.find_neighbor(command.args)
        if destination is None:
            known = self.world.find_location(command.args)
            if known and known.id != self.world.current_location:
                return [f"{known.name} is not directly reachable from here. Try 'map'."]
            return [f"There is no path to '{command.args}'. Paths lead to: {exits}."]

        world = self.world
        world.advance_time(TRAVEL_HOURS)
        if self.rng.random() < 0.3:
            world.weather = self.rng.choice(WEATHER)
        world.current_location = destination.id
        destination.visited = True
        world.add_journal(f"Travelled to {destination.name}.")
        lines = [
            f"You travel to {destination.name}. ({TRAVEL_HOURS} hours pass.)",
            f"== {destination.name} ==",
            self.narrator.describe_location(self._scene()),
            *self._surroundings(),
            *self._progress("visit", destination.id),
        ]
        if self._quest_foe(destination) or (
            destination.encounters
            and self.rng.random() < 0.2 + 0.1 * destination.danger
        ):
            lines += self._start_encounter(destination)
        return lines

    def _map(self, _: Command) -> list[str]:
        lines = ["Known places (* = you are here):"]
        for location in self.world.locations.values():
            if not location.visited:
                continue
            marker = "*" if location.id == self.world.current_location else " "
            paths = ", ".join(
                self._map_name(self.world.locations[key])
                for key in location.connections
            )
            lines.append(
                f"  {marker} {location.name} (danger {location.danger}) -> {paths}"
            )
        return lines

    def _map_name(self, location: Location) -> str:
        return location.name if location.visited else f"{location.name} (unexplored)"

    def _explore(self, _: Command) -> list[str]:
        location = self.world.location
        self.world.advance_time(EXPLORE_HOURS)
        if location.encounters and (
            self._quest_foe(location) or self.rng.random() < 0.4 + 0.1 * location.danger
        ):
            return self._start_encounter(location)
        if not location.safe and self.rng.random() < 0.4:
            gold = self.dice.roll(f"{location.danger + 1}d6").total
            self.player.gold += gold
            self.world.add_journal(
                f"Found {gold} gold while exploring {location.name}."
            )
            return [f"Searching the area, you find a hidden pouch with {gold} gold."]
        return self._do(Command("do", "", "search the surroundings carefully"))

    def _talk(self, command: Command) -> list[str]:
        here = self.world.npcs_at(self.world.current_location)
        if not here:
            return ["There is nobody here to talk to."]
        if not command.args:
            names = ", ".join(f"{npc.name} the {npc.occupation}" for npc in here)
            return [f"Talk to whom? People here: {names}."]
        npc, message = self._split_npc(command.args)
        if npc is None:
            return [f"There is nobody called '{command.args}' here."]

        narration = self.narrator.npc_reply(self._scene(), npc, message)
        npc.modify_disposition(narration.disposition_change)
        npc.remember(f"Player: {message or '(greeting)'} | {narration.text[:160]}")
        lines = [narration.text, *self._progress("talk", npc.key)]
        if npc is self._quest_giver() and not self.world.active_quests:
            lines += self._offer_quest(npc)
        return lines

    def _split_npc(self, text: str) -> tuple[NPC | None, str]:
        words = text.split()
        for size in range(len(words), 0, -1):
            npc = self.world.find_npc_here(" ".join(words[:size]))
            if npc:
                rest = words[size:]
                if rest and rest[0].lower() == "about":
                    rest = rest[1:]
                return npc, " ".join(rest)
        return None, ""

    def _attack(self, command: Command) -> list[str]:
        return self._combat_turn(lambda encounter: encounter.attack(command.args))

    def _dodge(self, _: Command) -> list[str]:
        return self._combat_turn(lambda encounter: encounter.dodge())

    def _flee(self, _: Command) -> list[str]:
        return self._combat_turn(lambda encounter: encounter.flee())

    def _use(self, command: Command) -> list[str]:
        if not command.args:
            return ["Use what? Try 'use healing potion'."]
        if self.encounter:
            return self._combat_turn(lambda encounter: encounter.use(command.args))
        key = find_item(command.args, list(self.player.inventory))
        if key and not ITEMS[key].healing:
            return self._do(command)
        return [use_item(self.player, command.args, self.dice)[1]]

    def _ability(self, command: Command) -> list[str]:
        if self.encounter:
            return self._combat_turn(lambda encounter: encounter.ability(command.args))
        try:
            return use_feature(self.player, self.dice)
        except FeatureUnavailable as error:
            return [str(error)]

    def _combat_turn(self, action: Callable[[Encounter], list[str]]) -> list[str]:
        return action(self.encounter) + self._after_combat_turn()

    def _start_encounter(self, location: Location) -> list[str]:
        monsters = [
            Monster.spawn(key, self.dice) for key in self._encounter_keys(location)
        ]
        _number_duplicates(monsters)
        self.encounter = Encounter(self.player, monsters, self.dice)
        names = ", ".join(monster.name for monster in monsters)
        return [
            f"!! Danger! {names} {'attacks' if len(monsters) == 1 else 'attack'}!"
        ] + (self.encounter.start() + self._after_combat_turn())

    def _encounter_keys(self, location: Location) -> list[str]:
        tier = player_tier(self.player.level)
        pool = [key for key in location.encounters if MONSTERS[key].tier <= tier] or [
            min(location.encounters, key=lambda key: MONSTERS[key].tier)
        ]
        count = 1 + (self.rng.random() < min(0.5, 0.15 * self.player.level))
        keys = [self.rng.choice(pool) for _ in range(count)]
        quest = self._quest_foe(location)
        return [quest.target, *keys[1:]] if quest else keys

    def _quest_foe(self, location: Location) -> Quest | None:
        return next(
            (
                quest
                for quest in self.world.active_quests
                if quest.objective == "defeat" and quest.location == location.id
            ),
            None,
        )

    def _after_combat_turn(self) -> list[str]:
        encounter = self.encounter
        if not encounter.over:
            return encounter.status() + [
                "Your turn: attack [enemy], dodge, flee, use <item>, ability [enemy]."
            ]
        self.encounter = None
        if encounter.defeat:
            return self._handle_defeat()
        if encounter.fled:
            self.world.add_journal(f"Fled from a fight at {self.world.location.name}.")
            return ["You catch your breath. The danger is behind you, for now."]
        return self._handle_victory(encounter)

    def _handle_victory(self, encounter: Encounter) -> list[str]:
        location = self.world.location
        gold = sum(max(1, enemy.xp // 10) for enemy in encounter.enemies)
        gold += self.dice.roll("1d6").total
        self.player.gold += gold
        names = ", ".join(enemy.name for enemy in encounter.enemies)
        self.world.add_journal(f"Defeated {names} at {location.name}.")
        lines = [
            f"*** Victory! You earn {encounter.xp_reward} XP and loot {gold} gold. ***"
        ]
        lines += self._award_xp(encounter.xp_reward)
        for key in {enemy.key for enemy in encounter.enemies}:
            lines += self._progress("defeat", key)
        return lines

    def _handle_defeat(self) -> list[str]:
        home = self.world.home
        lost = self.player.gold // 2
        self.player.gold -= lost
        self.player.hp = max(1, self.player.max_hp // 2)
        self.world.current_location = home.id
        self.world.advance_time(REST_HOURS)
        self.world.add_journal(f"Was defeated and carried back to {home.name}.")
        return [
            "!! You fall, and darkness takes you...",
            f"You wake in {home.name}, tended by kind strangers. "
            f"Someone helped themselves to {lost} of your gold.",
        ]

    def _award_xp(self, xp: int) -> list[str]:
        return [
            f"*** You reach level {level}! Max HP is now {self.player.max_hp}. ***"
            for level in self.player.gain_xp(xp)
        ]

    def _progress(self, objective: str, target: str) -> list[str]:
        lines = []
        for quest in complete_matching(
            self.world, objective, target, self.world.current_location
        ):
            self.player.gold += quest.reward_gold
            self.world.add_journal(f"Completed the quest '{quest.title}'.")
            lines.append(
                f"*** Quest complete: {quest.title}! "
                f"+{quest.reward_xp} XP, +{quest.reward_gold} gold. ***"
            )
            lines += self._award_xp(quest.reward_xp)
            giver = self._quest_giver()
            if giver and not self.world.active_quests:
                home = self.world.locations[giver.location].name
                lines.append(f"{giver.name} in {home} may have more work for you.")
        return lines

    def _quest_giver(self) -> NPC | None:
        return next(
            (npc for npc in self.world.npcs.values() if npc.occupation == "elder"), None
        )

    def _offer_quest(self, giver: NPC) -> list[str]:
        quest = create_quest(self.world, self.rng, giver, self.player.level)
        if quest is None:
            return [f'{giver.name} says: "You have done all we could ask. Thank you."']
        objective = objective_text(quest, self.world)
        quest.title, quest.description = self.narrator.name_quest(
            self._scene(), objective, giver
        )
        self.world.quests.append(quest)
        self.world.add_journal(f"Accepted the quest '{quest.title}' from {giver.name}.")
        return [
            f"*** New quest: {quest.title} ***",
            quest.description,
            f"Objective: {objective}. Reward: {quest.reward_xp} XP, {quest.reward_gold} gold.",
        ]

    def _quests(self, _: Command) -> list[str]:
        if not self.world.quests:
            return ["Your journal has no quests yet. Seek out the village elder."]
        lines = ["Quests:"]
        for quest in self.world.quests:
            mark = "[ ]" if quest.is_active else "[x]"
            lines.append(f"  {mark} {quest.title}: {objective_text(quest, self.world)}")
        return lines

    def _rest(self, _: Command) -> list[str]:
        location = self.world.location
        if not location.safe:
            if not self.player.remove_item("rations"):
                return [
                    "You need rations to camp in the wild. Buy some from a merchant."
                ]
            if location.encounters and self.rng.random() < 0.25:
                self.world.advance_time(REST_HOURS // 2)
                return [
                    "!! Your camp is disturbed in the night!"
                ] + self._start_encounter(location)
        self.world.advance_time(REST_HOURS)
        self.player.long_rest()
        self.world.add_journal(f"Rested at {location.name}.")
        return [
            f"You rest for {REST_HOURS} hours. HP {self.player.hp}/{self.player.max_hp}; "
            f"class feature uses restored. It is now day {self.world.day}, "
            f"{self.world.time_of_day}."
        ]

    def merchant(self) -> NPC | None:
        return next(
            (
                npc
                for npc in self.world.npcs_at(self.world.current_location)
                if npc.occupation == "merchant"
            ),
            None,
        )

    def _shop(self, _: Command) -> list[str]:
        merchant = self.merchant()
        if merchant is None:
            return ["There is no merchant here."]
        return [
            f"{merchant.name} shows you their wares (you have {self.player.gold} gold):"
        ] + [
            f"  {item.name}: {item.price} gold. {item.description}"
            for item in ITEMS.values()
        ]

    def _buy(self, command: Command) -> list[str]:
        if self.merchant() is None:
            return ["There is no merchant here."]
        words = command.args.split()
        quantity = int(words.pop(0)) if words and words[0].isdigit() else 1
        key = find_item(" ".join(words), list(ITEMS))
        if key is None or quantity < 1:
            return ["Buy what? Type 'shop' to see the wares."]
        cost = ITEMS[key].price * quantity
        if cost > self.player.gold:
            return [f"That costs {cost} gold, but you only have {self.player.gold}."]
        self.player.gold -= cost
        self.player.add_item(key, quantity)
        return [f"You buy {quantity} x {ITEMS[key].name} for {cost} gold."]

    def _check(self, command: Command) -> list[str]:
        name = command.args.strip().lower().replace(" ", "_")
        skill = find_match(name, list(SKILLS) + list(ABILITIES), lambda key: key)
        if skill is None:
            return ["Check which skill? For example: 'check perception'."]
        bonus = (
            self.player.skill_bonus(skill)
            if skill in SKILLS
            else self.player.modifier(skill)
        )
        roll = self.dice.d20(bonus)
        return [
            f"[{skill_label(skill)} check: {roll.natural} {bonus:+d} = {roll.total}]"
        ]

    def _roll(self, command: Command) -> list[str]:
        try:
            return [str(self.dice.roll(command.args or "d20"))]
        except ValueError as error:
            return [str(error)]

    def _do(self, command: Command) -> list[str]:
        action = command.raw
        scene = self._scene()
        narration = self.narrator.resolve_action(scene, action)
        lines = [narration.text]
        if narration.check:
            lines += self._skill_check(scene, action, narration.check)
        else:
            self.world.add_journal(f"Player: {action}")
        return lines

    def _skill_check(self, scene: Scene, action: str, check: CheckRequest) -> list[str]:
        bonus = self.player.skill_bonus(check.skill)
        roll = self.dice.d20(bonus)
        success = roll.total >= check.dc
        verdict = "success" if success else "failure"
        lines = [
            f"[{skill_label(check.skill)} check: {roll.natural} {bonus:+d} = "
            f"{roll.total} vs DC {check.dc}: {verdict}]",
            self.narrator.narrate_outcome(scene, action, check, roll.total, success),
        ]
        self.world.add_journal(f"Player tried to {action} ({verdict}).")
        if success:
            xp = check.dc // 2
            lines.append(f"(+{xp} XP)")
            lines += self._award_xp(xp)
        return lines

    def _save(self, command: Command) -> list[str]:
        name = command.args or self.player.name
        path = self.saves.save(name, self.player, self.world)
        return [f"Game saved to {path}."]

    def _load(self, command: Command) -> list[str]:
        if not command.args:
            names = ", ".join(self.saves.names()) or "none"
            return [f"Load which save? Available: {names}."]
        try:
            self.player, self.world = self.saves.load(command.args)
        except SaveError as error:
            return [str(error)]
        return [f"Loaded '{command.args}'."] + self._look(Command("look", "", "look"))

    def _quit(self, _: Command) -> list[str]:
        self.running = False
        if self.encounter:
            return [
                "You flee the table mid-fight. Progress since your last save is lost."
            ]
        path = self.saves.save(AUTOSAVE, self.player, self.world)
        return [f"Progress saved to {path}. Farewell, adventurer."]

    def _scene(self) -> Scene:
        world = self.world
        location = world.location
        player = self.player
        return Scene(
            character=(
                f"{player.name}, level {player.level} {player.race_info.name} "
                f"{player.class_info.name} ({player.hp}/{player.max_hp} HP)"
            ),
            location=location.name,
            description=location.description,
            danger=location.danger,
            time=f"day {world.day}, {world.time_of_day}",
            weather=world.weather,
            npcs=tuple(
                f"{npc.name} the {npc.occupation}" for npc in world.npcs_at(location.id)
            ),
            exits=tuple(neighbor.name for neighbor in world.neighbors()),
            quests=tuple(objective_text(quest, world) for quest in world.active_quests),
            journal=tuple(world.journal[-JOURNAL_CONTEXT:]),
        )


def _number_duplicates(monsters: list[Monster]) -> None:
    totals = Counter(monster.name for monster in monsters)
    seen: Counter[str] = Counter()
    for monster in monsters:
        base = monster.name
        if totals[base] > 1:
            seen[base] += 1
            monster.name = f"{base} {seen[base]}"
