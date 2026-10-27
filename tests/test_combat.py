import random

from core.character_creation import build_character
from core.combat_system import Encounter
from models.monster import Monster
from tests.helpers import fixed_dice
from utils.dice import Dice


def make_encounter(dice: Dice, *monster_keys: str) -> Encounter:
    hero = build_character("Kara", "human", "fighter")
    monsters = [Monster.spawn(key, dice) for key in monster_keys]
    encounter = Encounter(hero, monsters, dice)
    encounter.start()
    return encounter


def test_natural_twenty_always_hits_and_kills():
    encounter = make_encounter(fixed_dice(20), "goblin")
    lines = encounter.attack()
    assert "Critical hit!" in lines[0]
    assert encounter.victory
    assert encounter.xp_reward == 50


def test_natural_one_always_misses():
    encounter = make_encounter(fixed_dice(1), "giant rat")
    lines = encounter.attack()
    assert "misses" in lines[0]


def test_fight_eventually_ends():
    encounter = make_encounter(Dice(random.Random(3)), "goblin", "goblin")
    for _ in range(100):
        if encounter.over:
            break
        encounter.attack()
    assert encounter.over


def test_unknown_target_does_not_spend_turn():
    encounter = make_encounter(Dice(random.Random(5)), "wolf")
    round_before = encounter.round
    lines = encounter.attack("dragon")
    assert "no enemy called 'dragon'" in lines[0]
    assert encounter.round == round_before


def test_flee_succeeds_with_high_roll():
    encounter = make_encounter(fixed_dice(20), "orc")
    encounter.flee()
    assert encounter.fled and encounter.over


def test_feature_use_consumes_charge():
    dice = fixed_dice(10)
    hero = build_character("Ilsa", "elf", "wizard")
    encounter = Encounter(hero, [Monster.spawn("ogre", dice)], dice)
    encounter.start()
    lines = encounter.ability()
    assert "Three glowing darts" in lines[0]
    assert hero.feature_uses == hero.max_feature_uses - 1


def test_potion_heals_in_combat():
    encounter = make_encounter(fixed_dice(2), "giant rat")
    encounter.player.hp = 1
    lines = encounter.use("potion")
    assert "regain" in lines[0]
    assert encounter.player.inventory["healing potion"] == 1
