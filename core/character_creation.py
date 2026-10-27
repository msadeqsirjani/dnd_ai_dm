import random
from collections.abc import Sequence

from content.heroes import CLASSES, RACES
from content.items import STARTING_GOLD, STARTING_INVENTORY
from content.places import RACE_NAMES
from content.rules import STANDARD_ARRAY, ability_modifier
from models.character import Character
from utils.dice import Dice


def roll_ability_scores(dice: Dice) -> list[int]:
    return [dice.roll("4d6kh3").total for _ in range(6)]


def assign_scores(scores: Sequence[int], class_key: str) -> dict[str, int]:
    priorities = CLASSES[class_key].priorities
    return dict(zip(priorities, sorted(scores, reverse=True)))


def build_character(
    name: str, race_key: str, class_key: str, scores: Sequence[int] = STANDARD_ARRAY
) -> Character:
    abilities = assign_scores(scores, class_key)
    for ability, bonus in RACES[race_key].bonuses.items():
        abilities[ability] += bonus
    hp = max(
        1, CLASSES[class_key].hit_die + ability_modifier(abilities["constitution"])
    )
    character = Character(
        name=name,
        race=race_key,
        character_class=class_key,
        abilities=abilities,
        max_hp=hp,
        hp=hp,
        gold=STARTING_GOLD,
        inventory=dict(STARTING_INVENTORY),
    )
    character.feature_uses = character.max_feature_uses
    return character


def random_character(rng: random.Random) -> Character:
    race_key = rng.choice(list(RACES))
    first_names, _ = RACE_NAMES[race_key]
    return build_character(rng.choice(first_names), race_key, rng.choice(list(CLASSES)))
