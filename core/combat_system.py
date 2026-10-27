from core.attacks import describe_attack, resolve_attack
from core.class_features import FeatureUnavailable, feature_of, use_feature
from core.inventory import use_item
from models.character import Character
from models.monster import Monster
from utils.dice import Dice
from utils.matching import find_match

Combatant = Character | Monster


class Encounter:
    def __init__(self, player: Character, enemies: list[Monster], dice: Dice):
        self.player = player
        self.enemies = enemies
        self.dice = dice
        self.round = 1
        self.fled = False
        self._order: list[Combatant] = []
        self._turn = 0
        self._dodging = False

    @property
    def living_enemies(self) -> list[Monster]:
        return [enemy for enemy in self.enemies if enemy.is_alive]

    @property
    def victory(self) -> bool:
        return not self.living_enemies

    @property
    def defeat(self) -> bool:
        return not self.player.is_alive

    @property
    def over(self) -> bool:
        return self.victory or self.defeat or self.fled

    @property
    def xp_reward(self) -> int:
        return sum(enemy.xp for enemy in self.enemies)

    def start(self) -> list[str]:
        rolls = [
            (self.dice.d20(self.player.modifier("dexterity")).total, 1, self.player)
        ]
        rolls += [
            (self.dice.d20(enemy.dex_modifier).total, 0, enemy)
            for enemy in self.enemies
        ]
        rolls.sort(key=lambda entry: (entry[0], entry[1]), reverse=True)
        self._order = [combatant for _, _, combatant in rolls]
        lines = ["Roll for initiative!"]
        lines += [f"  {total:>2}  {combatant.name}" for total, _, combatant in rolls]
        return lines + self._run_until_player()

    def status(self) -> list[str]:
        enemies = ", ".join(
            f"{enemy.name} {enemy.hp}/{enemy.max_hp} HP"
            for enemy in self.living_enemies
        )
        return [
            f"Round {self.round}. You: {self.player.hp}/{self.player.max_hp} HP. "
            f"Enemies: {enemies}."
        ]

    def attack(self, target_query: str = "") -> list[str]:
        target = self._target(target_query)
        if target is None:
            return [self._no_target(target_query)]
        result = resolve_attack(
            self.dice, self.player.attack_bonus, self.player.damage, target
        )
        lines = [describe_attack(self.player.name, target, result)]
        return self._end_turn(lines + self._fallen(target))

    def dodge(self) -> list[str]:
        self._dodging = True
        return self._end_turn(
            ["You take the Dodge action. Attacks against you have disadvantage."]
        )

    def flee(self) -> list[str]:
        dc = 10 + len(self.living_enemies)
        roll = self.dice.d20(self.player.skill_bonus("acrobatics"))
        if roll.total >= dc:
            self.fled = True
            return [f"[Acrobatics {roll.total} vs DC {dc}] You break away and escape!"]
        return self._end_turn(
            [f"[Acrobatics {roll.total} vs DC {dc}] You try to flee but are cut off."]
        )

    def use(self, item_query: str) -> list[str]:
        used, message = use_item(self.player, item_query, self.dice)
        return self._end_turn([message]) if used else [message]

    def ability(self, target_query: str = "") -> list[str]:
        target = (
            self._target(target_query) if feature_of(self.player).needs_target else None
        )
        if feature_of(self.player).needs_target and target is None:
            return [self._no_target(target_query)]
        try:
            lines = use_feature(self.player, self.dice, target, in_combat=True)
        except FeatureUnavailable as error:
            return [str(error)]
        return self._end_turn(lines + (self._fallen(target) if target else []))

    def _target(self, query: str) -> Monster | None:
        living = self.living_enemies
        if not query:
            return living[0] if living else None
        return find_match(query, living, lambda enemy: enemy.name)

    def _no_target(self, query: str) -> str:
        names = ", ".join(enemy.name for enemy in self.living_enemies)
        return f"There is no enemy called '{query}'. Enemies: {names}."

    def _fallen(self, target: Monster) -> list[str]:
        return [] if target.is_alive else [f"{target.name} falls!"]

    def _end_turn(self, lines: list[str]) -> list[str]:
        if self.over:
            return lines
        self._advance()
        return lines + self._run_until_player()

    def _run_until_player(self) -> list[str]:
        lines = []
        while not self.over:
            actor = self._order[self._turn]
            if actor is self.player:
                self._dodging = False
                return lines
            if actor.is_alive:
                lines.append(self._monster_attack(actor))
            self._advance()
        return lines

    def _monster_attack(self, monster: Monster) -> str:
        result = resolve_attack(
            self.dice,
            monster.attack_bonus,
            monster.damage,
            self.player,
            disadvantage=self._dodging,
        )
        return describe_attack(monster.name, self.player, result)

    def _advance(self) -> None:
        self._turn = (self._turn + 1) % len(self._order)
        if self._turn == 0:
            self.round += 1
