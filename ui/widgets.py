from rich import box
from rich.console import Group
from rich.markup import escape
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.tree import Tree

from content.items import ITEMS
from content.rules import ABILITIES, XP_THRESHOLDS, skill_label
from core.class_features import feature_of
from core.commands import HELP
from core.quests import objective_text
from models.character import Character
from models.world_state import Location, WorldState
from ui.art import LOCATION_ICONS

BAR_WIDTH = 18
MAX_DANGER = 3


def bar(
    current: int,
    maximum: int,
    color: str | None = None,
    label: str | None = None,
    width: int = BAR_WIDTH,
) -> Text:
    ratio = current / maximum if maximum else 0
    filled = round(max(0.0, min(1.0, ratio)) * width)
    if color is None:
        color = "green" if ratio > 0.5 else "yellow" if ratio > 0.25 else "red"
    text = Text("█" * filled, style=color)
    text.append("░" * (width - filled), style="grey35")
    text.append(f" {label or f'{current}/{maximum}'}", style="bold")
    return text


def pips(current: int, maximum: int) -> Text:
    text = Text("●" * current, style="bold magenta")
    text.append("○" * max(0, maximum - current), style="grey50")
    return text


def icon(location: Location) -> str:
    return LOCATION_ICONS.get(location.kind, "•")


def danger(location: Location) -> Text:
    if location.safe:
        return Text("safe", style="green")
    text = Text("●" * location.danger, style="red")
    text.append("○" * (MAX_DANGER - location.danger), style="grey42")
    return text


def xp_bar(character: Character) -> Text:
    floor = XP_THRESHOLDS[character.level - 1]
    ceiling = character.xp_to_next
    if ceiling is None:
        return bar(1, 1, "blue", f"{character.xp} (max level)")
    return bar(
        character.xp - floor, ceiling - floor, "blue", f"{character.xp}/{ceiling}"
    )


def character_view(character: Character) -> Panel:
    cls = character.class_info
    feature = feature_of(character)
    vitals = Table.grid(padding=(0, 2))
    vitals.add_column(style="bold", no_wrap=True)
    vitals.add_column()
    vitals.add_row("HP", bar(character.hp, character.max_hp))
    vitals.add_row("XP", xp_bar(character))
    vitals.add_row(
        "Defense",
        Text(f"AC {character.armor_class}   Proficiency +{character.proficiency}"),
    )
    vitals.add_row(
        "Weapon",
        Text(
            f"{character.weapon.name}: {character.attack_bonus:+d} to hit, "
            f"{character.damage} damage"
        ),
    )
    feature_text = Text(f"{feature.name} ")
    feature_text.append_text(pips(character.feature_uses, character.max_feature_uses))
    feature_text.append(f"\n{feature.description}", style="italic grey70")
    vitals.add_row("Feature", feature_text)

    abilities = Table(box=box.SIMPLE_HEAD, show_edge=False, header_style="bold cyan")
    for ability in ABILITIES:
        abilities.add_column(ability[:3].upper(), justify="center")
    abilities.add_row(
        *(
            f"{character.abilities[ability]} ({character.modifier(ability):+d})"
            for ability in ABILITIES
        )
    )

    skills = Text("Proficient skills: ", style="bold")
    skills.append(
        ", ".join(
            f"{skill_label(skill)} {character.skill_bonus(skill):+d}"
            for skill in cls.skills
        ),
        style="not bold",
    )
    return Panel(
        Group(vitals, Text(""), abilities, skills),
        title=f"[bold]{escape(character.name)}[/] · Level {character.level} "
        f"{character.race_info.name} {cls.name}",
        border_style="green",
        box=box.ROUNDED,
    )


def inventory_view(character: Character) -> Panel:
    table = Table(box=box.SIMPLE_HEAVY, header_style="bold cyan", expand=True)
    table.add_column("Qty", justify="right", style="bold")
    table.add_column("Item", style="bold")
    table.add_column("Description", style="grey70")
    for key, quantity in sorted(character.inventory.items()):
        table.add_row(str(quantity), ITEMS[key].name, ITEMS[key].description)
    if not character.inventory:
        table.add_row("", "Your pack is empty.", "")
    return Panel(
        table,
        title="🎒 Inventory",
        subtitle=f"[yellow]💰 {character.gold} gold[/]",
        border_style="yellow",
    )


def shop_view(character: Character, merchant_name: str) -> Panel:
    table = Table(box=box.SIMPLE_HEAVY, header_style="bold cyan", expand=True)
    table.add_column("Item", style="bold")
    table.add_column("Price", justify="right", style="yellow")
    table.add_column("Description", style="grey70")
    for item in ITEMS.values():
        affordable = item.price <= character.gold
        table.add_row(
            item.name,
            f"{item.price} gold",
            item.description,
            style=None if affordable else "dim",
        )
    return Panel(
        table,
        title=f"🛒 {merchant_name}'s wares",
        subtitle=f"[yellow]You have {character.gold} gold · buy [quantity] <item>[/]",
        border_style="yellow",
    )


def quests_view(world: WorldState) -> Panel:
    table = Table(box=box.SIMPLE_HEAVY, header_style="bold cyan", expand=True)
    table.add_column("", width=2)
    table.add_column("Quest", style="bold")
    table.add_column("Objective")
    table.add_column("Reward", style="yellow", justify="right")
    for quest in sorted(world.quests, key=lambda quest: not quest.is_active):
        table.add_row(
            "★" if quest.is_active else "✓",
            quest.title,
            objective_text(quest, world),
            f"{quest.reward_xp} XP · {quest.reward_gold} gold",
            style=None if quest.is_active else "dim strike",
        )
    if not world.quests:
        table.add_row("", "No quests yet", "Talk to the village elder.", "")
    return Panel(table, title="📜 Quest journal", border_style="yellow")


def map_view(world: WorldState) -> Panel:
    quest_places = {quest.location for quest in world.active_quests}
    home = world.home
    tree = Tree(_map_label(world, home, quest_places), guide_style="grey50")
    seen = {home.id}
    frontier = [(home, tree)]
    while frontier:
        location, node = frontier.pop(0)
        for key in location.connections:
            if key in seen:
                continue
            seen.add(key)
            neighbor = world.locations[key]
            child = node.add(_map_label(world, neighbor, quest_places))
            if neighbor.visited:
                frontier.append((neighbor, child))
    legend = Text(
        "📍 you are here    ★ quest target    ? unexplored    ●●○ danger",
        style="grey62",
    )
    return Panel(
        Group(tree, Text(""), legend), title="🌍 World map", border_style="blue"
    )


def _map_label(world: WorldState, location: Location, quest_places: set[str]) -> Text:
    here = location.id == world.current_location
    if not location.visited:
        label = Text(f"? {location.name}", style="grey50 italic")
    else:
        label = Text(
            f"{icon(location)} {location.name}", style="bold cyan" if here else "bold"
        )
    label.append("  ")
    label.append_text(danger(location))
    if location.id in quest_places:
        label.append("  ★", style="bold yellow")
    if here:
        label.append("  📍 you are here", style="bold cyan")
    return label


def help_view() -> Panel:
    table = Table(box=box.SIMPLE_HEAVY, header_style="bold cyan", expand=True)
    table.add_column("Command", style="bold green", no_wrap=True)
    table.add_column("What it does")
    for usage, description in HELP:
        table.add_row(usage, description)
    return Panel(table, title="❓ Commands", border_style="cyan")
