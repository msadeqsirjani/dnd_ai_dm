import re

from rich import box
from rich.align import Align
from rich.console import Group, RenderableType
from rich.layout import Layout
from rich.markup import escape
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.tree import Tree

from core.class_features import feature_of
from core.commands import COMBAT_VERBS, parse
from core.game_manager import GameManager
from core.quests import objective_text
from ui.art import LOCATION_ART, LOCATION_COLORS, MONSTER_ART
from ui.console import Console, styled
from ui.widgets import (
    bar,
    character_view,
    danger,
    help_view,
    icon,
    inventory_view,
    map_view,
    pips,
    quests_view,
    shop_view,
    xp_bar,
)

EXPLORE_HINTS = (
    "go <place>",
    "explore",
    "talk <name>",
    "quests",
    "map",
    "stats",
    "rest",
    "help",
)
COMBAT_HINTS = ("attack", "ability", "use potion", "dodge", "flee")
REDUNDANT_PREFIXES = (
    "== ",
    "People here:",
    "Paths lead to:",
    "Your turn:",
    "Type 'help'",
)
STATUS_LINE = re.compile(r"^Round \d+\. You: ")
MAX_WIDTH = 120
MIN_FULL_SCREEN_HEIGHT = 24
MIN_STORY_ROWS = 6
FRAME_BORDER = 2
PANEL_CHROME = 4
LOG_LIMIT = 300


class Screen:
    def __init__(self, console: Console, game: GameManager):
        self.console = console
        self.game = game
        self._log: list[tuple[int, Text]] = []
        self._turn = 0

    def ask(self) -> str:
        return self.console.ask("❯ ")

    def show(self, lines: list[str], command_text: str = "") -> None:
        self._record(lines, command_text)
        view = self._view(parse(command_text).verb)
        rich = self.console.rich
        width = min(rich.width, MAX_WIDTH)
        inner = width - FRAME_BORDER
        height = rich.height - 1

        hints = self._hints()
        hints_height = self._height(hints, inner)
        top = [self._header()] if view else [self._header(), self._status(inner)]
        top_heights = [self._height(part, inner) for part in top]
        body_rows = height - FRAME_BORDER - sum(top_heights) - hints_height
        if view is not None and self._height(view, inner) > body_rows:
            top, top_heights = [], []
            body_rows = height - FRAME_BORDER - hints_height

        self.console.clear()
        if height < MIN_FULL_SCREEN_HEIGHT or body_rows < MIN_STORY_ROWS:
            story = view or self._story(None, width - PANEL_CHROME)
            compact = Group(self._header(), self._status(width), story, hints)
            self.console.render(Align.center(compact, width=width))
            return

        body = view or self._story(body_rows, inner - PANEL_CHROME)
        layout = Layout()
        layout.split_column(
            *(Layout(part, size=size) for part, size in zip(top, top_heights)),
            Layout(body),
            Layout(hints, size=hints_height),
        )
        frame = Panel(
            layout,
            title="[bold yellow]🐉 AI Dungeon Master 🐉[/]",
            border_style="yellow",
            box=box.DOUBLE,
            width=width,
            height=height,
            padding=0,
        )
        self.console.render(Align.center(frame))

    def _height(self, renderable: RenderableType, width: int) -> int:
        rich = self.console.rich
        options = rich.options.update(width=width, height=None)
        return len(rich.render_lines(renderable, options, pad=False))

    def _record(self, lines: list[str], command_text: str) -> None:
        self._turn += 1
        if command_text.strip():
            self._log.append(
                (self._turn, Text(f"❯ {command_text.strip()}", style="bold green"))
            )
        self._log += [
            (self._turn, self._story_line(line))
            for line in lines
            if not _redundant(line)
        ]
        self._log = self._log[-LOG_LIMIT:]

    def _view(self, verb: str) -> RenderableType | None:
        game = self.game
        if game.encounter and verb not in COMBAT_VERBS:
            return None
        if verb == "stats":
            return character_view(game.player)
        if verb == "inventory":
            return inventory_view(game.player)
        if verb == "quests":
            return quests_view(game.world)
        if verb == "map":
            return map_view(game.world)
        if verb == "help":
            return help_view()
        if verb == "shop" and game.merchant():
            return shop_view(game.player, game.merchant().name)
        return None

    def _header(self) -> Panel:
        world = self.game.world
        location = world.location
        encounter = self.game.encounter
        subtitle = f"Day {world.day} · {world.time_of_day} · {world.weather}"
        if encounter and encounter.living_enemies:
            foe = encounter.living_enemies[0]
            names = ", ".join(enemy.name for enemy in encounter.living_enemies)
            verb = "stands" if len(encounter.living_enemies) == 1 else "stand"
            body = Group(
                Text(f"{names} {verb} against you!", style="bold red"),
                Text(f"Round {encounter.round} of battle at {location.name}."),
            )
            return self._art_panel(
                MONSTER_ART.get(foe.key, ""),
                "red",
                body,
                f"👹 Combat at {location.name}",
                subtitle,
                "red",
            )
        people = ", ".join(
            f"{npc.name} the {npc.occupation}" for npc in world.npcs_at(location.id)
        )
        body = Group(
            Text(location.description),
            Text(""),
            Text.assemble(("People here: ", "bold"), people or "nobody"),
        )
        color = LOCATION_COLORS.get(location.kind, "white")
        return self._art_panel(
            LOCATION_ART.get(location.kind, ""),
            color,
            body,
            f"{icon(location)} {location.name}",
            subtitle,
            color,
        )

    def _art_panel(
        self,
        art: str,
        art_style: str,
        body: RenderableType,
        title: str,
        subtitle: str,
        border: str,
    ) -> Panel:
        grid = Table.grid(padding=(0, 3), expand=True)
        grid.add_column(no_wrap=True)
        grid.add_column(ratio=1, vertical="middle")
        grid.add_row(Text(art.strip("\n"), style=art_style), body)
        return Panel(
            grid,
            title=f"[bold]{escape(title)}[/]",
            subtitle=subtitle,
            border_style=border,
            box=box.HEAVY,
        )

    def _status(self, width: int) -> Table:
        column = (width - 1) // 2
        hero = self._hero()
        side = self._enemies() if self.game.encounter else self._paths()
        tallest = max(self._height(hero, column), self._height(side, column))
        hero.height = side.height = tallest
        grid = Table.grid(expand=True, padding=(0, 1, 0, 0))
        grid.add_column(ratio=1)
        grid.add_column(ratio=1)
        grid.add_row(hero, side)
        return grid

    def _hero(self) -> Panel:
        player = self.game.player
        world = self.game.world
        table = Table.grid(padding=(0, 2))
        table.add_column(no_wrap=True)
        table.add_column()
        table.add_row(Text("HP", style="bold red"), bar(player.hp, player.max_hp))
        table.add_row(Text("XP", style="bold blue"), xp_bar(player))
        table.add_row(
            Text("AC", style="bold"),
            Text.assemble(
                (str(player.armor_class), "bold"),
                ("    Gold ", "bold"),
                (str(player.gold), "yellow"),
                ("    Potions ", "bold"),
                (str(player.inventory.get("healing potion", 0)), "red"),
            ),
        )
        table.add_row(
            Text("Power", style="bold magenta"),
            Text.assemble(
                (f"{feature_of(player).name}  ", ""),
                pips(player.feature_uses, player.max_feature_uses),
            ),
        )
        quest = next(iter(world.active_quests), None)
        goal = objective_text(quest, world) if quest else "Talk to the village elder"
        table.add_row(
            Text("Goal", style="bold yellow"), Text(goal, style="italic yellow")
        )
        title = (
            f"[bold]{escape(player.name)}[/] · Level {player.level} "
            f"{player.race_info.name} {player.class_info.name}"
        )
        return Panel(table, title=title, border_style="green", box=box.ROUNDED)

    def _paths(self) -> Panel:
        world = self.game.world
        quest_places = {quest.location for quest in world.active_quests}
        tree = Tree(
            Text(f"📍 {world.location.name}", style="bold cyan"), guide_style="blue"
        )
        for location in world.neighbors():
            label = Text(f"{icon(location)} {location.name}  ", style="bold")
            label.append_text(danger(location))
            if not location.visited:
                label.append("  new", style="cyan italic")
            if location.id in quest_places:
                label.append("  ★ quest", style="bold yellow")
            tree.add(label)
        return Panel(
            tree, title="👣 Paths from here", border_style="blue", box=box.ROUNDED
        )

    def _enemies(self) -> Panel:
        encounter = self.game.encounter
        table = Table.grid(padding=(0, 2))
        table.add_column(no_wrap=True)
        table.add_column()
        for enemy in encounter.enemies:
            if enemy.is_alive:
                table.add_row(
                    Text(f"👹 {enemy.name}", style="bold red"),
                    bar(enemy.hp, enemy.max_hp, "red", width=12),
                )
                table.add_row("", Text(f"AC {enemy.armor_class}", style="grey62"))
            else:
                table.add_row(
                    Text(f"💀 {enemy.name}", style="dim strike"),
                    Text("defeated", style="dim"),
                )
        return Panel(
            table,
            title=f"👹 Enemies · round {encounter.round}",
            border_style="red",
            box=box.ROUNDED,
        )

    def _story(self, rows: int | None, width: int) -> Panel:
        capacity = None if rows is None else rows - 2
        picked: list[Text] = []
        used = 0
        for turn, text in reversed(self._log):
            if capacity is None and turn != self._turn:
                break
            needed = self._height(text, width)
            if capacity is not None and used + needed > capacity:
                break
            line = text.copy()
            if turn != self._turn:
                line.stylize("grey50")
            picked.append(line)
            used += needed
        body = Group(*reversed(picked)) if picked else Text("…", style="dim")
        return Panel(
            body,
            title="📖 Story",
            border_style="grey50",
            box=box.ROUNDED,
            height=rows,
        )

    def _story_line(self, line: str) -> Text:
        name = self.game.player.name
        if line.startswith(f"{name} hits") or line.endswith("falls!"):
            return Text(f"🎯 {line}", style="bold green")
        if f" hits {name} " in line:
            return Text(f"💥 {line}", style="bold red")
        if " misses." in line:
            return Text(f"💨 {line}", style="grey62")
        if line.startswith("[") and line.rstrip().endswith("success]"):
            return Text(f"🎲 {line}", style="bold green")
        if line.startswith("[") and line.rstrip().endswith("failure]"):
            return Text(f"🎲 {line}", style="bold red")
        if line.startswith("["):
            return Text(f"🎲 {line}", style="magenta")
        if line == "Roll for initiative!":
            return Text(f"🎲 {line}", style="bold magenta")
        return styled(line)

    def _hints(self) -> Text:
        hints = COMBAT_HINTS if self.game.encounter else EXPLORE_HINTS
        text = Text(" ")
        for command in hints:
            text.append(f" {command} ", style="bold black on green")
            text.append("  ")
        if not self.game.encounter:
            text.append("\n  …or type any action, like ", style="grey62")
            text.append("search the old well", style="italic")
        return text


def _redundant(line: str) -> bool:
    return line.startswith(REDUNDANT_PREFIXES) or bool(STATUS_LINE.match(line))
