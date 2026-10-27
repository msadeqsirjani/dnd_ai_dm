import random

import pytest

from core.character_creation import build_character
from core.game_manager import GameManager
from core.narrator import OfflineNarrator
from core.persistence import SaveError, SaveStore


@pytest.fixture
def game(tmp_path):
    rng = random.Random(11)
    hero = build_character("Tamsin", "human", "fighter")
    return GameManager.new_game(hero, OfflineNarrator(rng), rng, SaveStore(tmp_path))


def test_opening_offers_a_quest(game):
    lines = game.opening()
    assert any(line.startswith("*** New quest") for line in lines)
    assert len(game.world.active_quests) == 1


def test_travel_moves_player_and_passes_time(game):
    destination = game.world.neighbors()[0]
    game.handle(f"go {destination.name}")
    assert game.world.current_location == destination.id
    assert game.world.hour == 10


def test_unknown_destination(game):
    assert "no path" in game.handle("go to atlantis")[0]


def test_combat_only_commands_are_blocked_in_combat(game):
    game.world.current_location = next(
        loc.id for loc in game.world.locations.values() if loc.encounters
    )
    game._start_encounter(game.world.location)
    if game.encounter:
        assert "middle of a fight" in game.handle("map")[0]


def test_a_fight_resolves_to_victory_or_defeat(game):
    location = next(loc for loc in game.world.locations.values() if loc.encounters)
    game.world.current_location = location.id
    game._start_encounter(location)
    for _ in range(100):
        if not game.encounter:
            break
        game.handle("attack")
    assert game.encounter is None
    assert game.player.xp > 0 or game.world.location.safe


def test_freeform_action_can_trigger_skill_check(game):
    lines = game.handle("climb the old well")
    assert any(line.startswith("[Athletics check") for line in lines)


def test_shop_and_buy(game):
    game.player.gold = 100
    lines = game.handle("buy 2 rations")
    assert "for 10 gold" in lines[0]
    assert game.player.inventory["rations"] == 5


def test_save_and_load_round_trip(game):
    game.opening()
    game.handle("save slot one")
    game.player.gold = 0
    game.handle("load slot one")
    assert game.player.gold > 0
    assert game.world.active_quests


def test_loading_missing_save_reports_error(game):
    assert "No saved game" in game.handle("load nowhere")[0]


def test_quit_autosaves(game, tmp_path):
    game.handle("quit")
    assert not game.running
    assert (tmp_path / "autosave.json").exists()


def test_from_save_missing_raises(tmp_path):
    with pytest.raises(SaveError):
        GameManager.from_save(
            SaveStore(tmp_path),
            "ghost",
            OfflineNarrator(random.Random()),
            random.Random(),
        )
