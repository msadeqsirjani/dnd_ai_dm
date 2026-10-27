from collections.abc import Callable

from content.heroes import FEATURES, Feature
from core.attacks import describe_attack, resolve_attack
from models.character import Character
from models.monster import Monster
from utils.dice import Dice


class FeatureUnavailable(Exception):
    pass


def feature_of(character: Character) -> Feature:
    return FEATURES[character.class_info.feature]


def use_feature(
    character: Character,
    dice: Dice,
    target: Monster | None = None,
    in_combat: bool = False,
) -> list[str]:
    feature = feature_of(character)
    if character.feature_uses <= 0:
        raise FeatureUnavailable(
            f"You have no uses of {feature.name} left. Take a long rest to recover."
        )
    if feature.combat_only and not in_combat:
        raise FeatureUnavailable(f"{feature.name} can only be used in combat.")
    if feature.needs_target and target is None:
        raise FeatureUnavailable(f"{feature.name} needs a target.")
    character.feature_uses -= 1
    return _HANDLERS[character.class_info.feature](character, dice, target)


def _healed(character: Character, amount: int, source: str) -> list[str]:
    healed = character.heal(max(1, amount))
    return [f"{source} restores {healed} HP. ({character.hp}/{character.max_hp} HP)"]


def _second_wind(character: Character, dice: Dice, _: Monster | None) -> list[str]:
    roll = dice.roll(f"1d10+{character.level}")
    return _healed(character, roll.total, "You dig deep. Second Wind")


def _cure_wounds(character: Character, dice: Dice, _: Monster | None) -> list[str]:
    roll = dice.roll(f"1d8{character.modifier('wisdom'):+d}")
    return _healed(character, roll.total, "Divine light washes over you. Cure Wounds")


def _cunning_strike(
    character: Character, dice: Dice, target: Monster | None
) -> list[str]:
    result = resolve_attack(
        dice,
        character.attack_bonus,
        character.damage,
        target,
        advantage=True,
        extra_damage=f"{(character.level + 1) // 2}d6",
    )
    return [
        "You feint, then strike from an unexpected angle.",
        describe_attack(character.name, target, result),
    ]


def _magic_missile(
    character: Character, dice: Dice, target: Monster | None
) -> list[str]:
    dealt = target.take_damage(dice.roll("3d4+3").total)
    return [f"Three glowing darts streak into {target.name} for {dealt} force damage."]


_HANDLERS: dict[str, Callable[[Character, Dice, Monster | None], list[str]]] = {
    "second_wind": _second_wind,
    "cure_wounds": _cure_wounds,
    "cunning_strike": _cunning_strike,
    "magic_missile": _magic_missile,
}
