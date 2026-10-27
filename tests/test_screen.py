import io
import random

import pytest
from rich.cells import cell_len
from rich.console import Console as RichConsole

from core.character_creation import build_character
from core.game_manager import GameManager
from core.narrator import OfflineNarrator
from core.persistence import SaveStore
from ui.character_wizard import create_character
from ui.console import Console
from ui.screen import Screen
from utils.dice import Dice


def recording_console(answers=()) -> Console:
    console = Console(RichConsole(file=io.StringIO(), width=100, record=True))
    replies = iter(answers)
    console.ask = lambda prompt: next(replies)
    return console


def text_of(console: Console) -> str:
    return console.rich.export_text()


@pytest.fixture
def screen(tmp_path):
    rng = random.Random(7)
    hero = build_character("Kara", "human", "fighter")
    game = GameManager.new_game(hero, OfflineNarrator(rng), rng, SaveStore(tmp_path))
    return Screen(recording_console(), game)


def test_exploration_screen_shows_panels(screen):
    screen.show(screen.game.opening())
    output = text_of(screen.console)
    assert "Paths from here" in output
    assert "Kara · Level 1 Human Fighter" in output
    assert "New quest" in output


@pytest.mark.parametrize(
    "command, title",
    [
        ("stats", "Proficient skills"),
        ("inventory", "Inventory"),
        ("quests", "Quest journal"),
        ("map", "World map"),
        ("help", "Commands"),
        ("shop", "wares"),
    ],
)
def test_info_commands_render_views(screen, command, title):
    screen.game.opening()
    screen.show(screen.game.handle(command), command)
    assert title in text_of(screen.console)


def test_combat_screen_shows_enemies(screen):
    game = screen.game
    location = next(loc for loc in game.world.locations.values() if loc.encounters)
    game.world.current_location = location.id
    lines = game._start_encounter(location)
    screen.show(lines)
    output = text_of(screen.console)
    assert "Combat" in output or "fall" in output


def test_wizard_builds_character_from_answers():
    console = recording_console(["Nim", "2", "wizard", "1", ""])
    hero = create_character(console, Dice(random.Random(1)))
    assert (hero.name, hero.race, hero.character_class) == ("Nim", "elf", "wizard")
    assert "Choose a class" in text_of(console)


def test_full_screen_layout_is_capped_and_centered(tmp_path):
    rng = random.Random(7)
    hero = build_character("Kara", "human", "fighter")
    game = GameManager.new_game(hero, OfflineNarrator(rng), rng, SaveStore(tmp_path))
    console = Console(
        RichConsole(file=io.StringIO(), width=200, height=50, record=True)
    )
    screen = Screen(console, game)
    screen.show(game.opening())
    screen.show(game.handle("look"), "look")
    lines = text_of(console).splitlines()
    frame = [line for line in lines if "AI Dungeon Master" in line][-1]
    assert cell_len(frame.strip()) == 120
    assert frame.startswith(" " * 40)
    assert any("❯ look" in line for line in lines)


@pytest.mark.parametrize("size", [(80, 24), (100, 30), (120, 40), (200, 50)])
@pytest.mark.parametrize(
    "commands",
    [
        ["look"],
        ["help"],
        ["map"],
        ["stats"],
        ["climb the well"] * 12,
    ],
)
def test_every_rendered_row_fits_the_terminal(tmp_path, size, commands):
    width, height = size
    rng = random.Random(7)
    hero = build_character("Kara", "human", "fighter")
    game = GameManager.new_game(hero, OfflineNarrator(rng), rng, SaveStore(tmp_path))
    console = Console(
        RichConsole(file=io.StringIO(), width=width, height=height, record=True)
    )
    screen = Screen(console, game)
    screen.show(game.opening())
    for command in commands:
        console.rich.export_text(clear=True)
        screen.show(game.handle(command), command)
    rows = console.rich.export_text().splitlines()
    assert all(cell_len(row) <= width for row in rows)
    if height >= 30:
        assert len(rows) <= height - 1
