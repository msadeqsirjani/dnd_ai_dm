from rich import box
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from content.heroes import CLASSES, FEATURES, RACES, WEAPONS
from content.rules import STANDARD_ARRAY
from core.character_creation import build_character, roll_ability_scores
from models.character import Character
from ui.console import Console
from ui.widgets import character_view
from utils.dice import Dice
from utils.matching import find_match


def create_character(console: Console, dice: Dice) -> Character:
    console.render(
        Panel(
            Text("Forge your hero", style="bold yellow", justify="center"),
            box=box.DOUBLE,
            border_style="yellow",
        )
    )
    name = console.ask("👤 What is your hero's name? ").strip() or "Adventurer"
    race = _choose(console, "👥 Choose a race", list(RACES), _race_table())
    class_key = _choose(console, "🎯 Choose a class", list(CLASSES), _class_table())
    method = _choose(
        console, "🎲 Ability scores", ["standard", "roll"], _method_table()
    )
    scores = STANDARD_ARRAY if method == "standard" else roll_ability_scores(dice)
    if method == "roll":
        rolled = ", ".join(map(str, sorted(scores, reverse=True)))
        console.render(Text(f"🎲 You rolled: {rolled}", style="bold magenta"))
    character = build_character(name, race, class_key, scores)
    console.render(character_view(character))
    console.ask("Press Enter to begin your adventure… ")
    return character


def _race_table() -> Table:
    table = _table("#", "Race", "Bonuses")
    for index, race in enumerate(RACES.values(), 1):
        bonuses = ", ".join(
            f"{ability[:3].upper()} +{bonus}" for ability, bonus in race.bonuses.items()
        )
        table.add_row(str(index), race.name, bonuses)
    return table


def _class_table() -> Table:
    table = _table("#", "Class", "HP die", "Weapon", "Armor", "Power")
    for index, cls in enumerate(CLASSES.values(), 1):
        feature = FEATURES[cls.feature]
        table.add_row(
            str(index),
            cls.name,
            f"d{cls.hit_die}",
            WEAPONS[cls.weapon].name,
            f"AC {cls.base_armor}",
            Text.assemble(
                (feature.name, "bold magenta"),
                (f"\n{feature.description}", "grey70"),
            ),
        )
    return table


def _method_table() -> Table:
    table = _table("#", "Method", "Scores")
    table.add_row("1", "Standard array", ", ".join(map(str, STANDARD_ARRAY)))
    table.add_row("2", "Roll", "4d6, drop the lowest die, six times")
    return table


def _table(*headers: str) -> Table:
    table = Table(box=box.ROUNDED, header_style="bold cyan", border_style="grey50")
    for header in headers:
        table.add_column(header, style="bold" if header != "#" else "yellow")
    return table


def _choose(console: Console, title: str, keys: list[str], table: Table) -> str:
    table.title = title
    table.title_style = "bold yellow"
    console.render(table)
    while True:
        answer = console.ask("❯ ").strip().lower()
        if answer.isdigit() and 1 <= int(answer) <= len(keys):
            return keys[int(answer) - 1]
        match = find_match(answer, keys, lambda key: key)
        if match:
            return match
        console.render(
            Text("Pick one of the listed options by number or name.", style="yellow")
        )
