from dataclasses import dataclass

from content.rules import ABILITIES


@dataclass(frozen=True)
class Weapon:
    name: str
    damage: str
    ability: str


@dataclass(frozen=True)
class Race:
    name: str
    bonuses: dict[str, int]


@dataclass(frozen=True)
class Feature:
    name: str
    description: str
    needs_target: bool
    combat_only: bool


@dataclass(frozen=True)
class CharacterClass:
    name: str
    hit_die: int
    priorities: tuple[str, ...]
    weapon: str
    base_armor: int
    dex_cap: int | None
    skills: tuple[str, ...]
    saving_throws: tuple[str, ...]
    feature: str
    feature_uses: int
    feature_scales: bool


WEAPONS = {
    "longsword": Weapon("Longsword", "1d8", "strength"),
    "greataxe": Weapon("Greataxe", "1d12", "strength"),
    "mace": Weapon("Mace", "1d6", "strength"),
    "shortsword": Weapon("Shortsword", "1d6", "finesse"),
    "dagger": Weapon("Dagger", "1d4", "finesse"),
    "fire bolt": Weapon("Fire Bolt", "1d10", "intelligence"),
}

RACES = {
    "human": Race("Human", {ability: 1 for ability in ABILITIES}),
    "elf": Race("Elf", {"dexterity": 2, "intelligence": 1}),
    "dwarf": Race("Dwarf", {"constitution": 2, "wisdom": 1}),
    "halfling": Race("Halfling", {"dexterity": 2, "charisma": 1}),
    "half-orc": Race("Half-Orc", {"strength": 2, "constitution": 1}),
}

FEATURES = {
    "second_wind": Feature(
        "Second Wind", "Regain 1d10 + your level in hit points.", False, False
    ),
    "cunning_strike": Feature(
        "Cunning Strike",
        "Attack with advantage; a hit deals an extra 1d6 per two levels.",
        True,
        True,
    ),
    "magic_missile": Feature(
        "Magic Missile",
        "Three darts automatically hit one enemy for 3d4 + 3 force damage.",
        True,
        True,
    ),
    "cure_wounds": Feature(
        "Cure Wounds", "Regain 1d8 + your Wisdom modifier in hit points.", False, False
    ),
}

CLASSES = {
    "fighter": CharacterClass(
        name="Fighter",
        hit_die=10,
        priorities=(
            "strength",
            "constitution",
            "dexterity",
            "wisdom",
            "charisma",
            "intelligence",
        ),
        weapon="longsword",
        base_armor=16,
        dex_cap=0,
        skills=("athletics", "intimidation", "perception", "survival"),
        saving_throws=("strength", "constitution"),
        feature="second_wind",
        feature_uses=1,
        feature_scales=False,
    ),
    "rogue": CharacterClass(
        name="Rogue",
        hit_die=8,
        priorities=(
            "dexterity",
            "constitution",
            "charisma",
            "wisdom",
            "intelligence",
            "strength",
        ),
        weapon="shortsword",
        base_armor=11,
        dex_cap=None,
        skills=(
            "stealth",
            "acrobatics",
            "sleight_of_hand",
            "deception",
            "investigation",
            "perception",
        ),
        saving_throws=("dexterity", "intelligence"),
        feature="cunning_strike",
        feature_uses=2,
        feature_scales=False,
    ),
    "wizard": CharacterClass(
        name="Wizard",
        hit_die=6,
        priorities=(
            "intelligence",
            "constitution",
            "dexterity",
            "wisdom",
            "charisma",
            "strength",
        ),
        weapon="fire bolt",
        base_armor=10,
        dex_cap=None,
        skills=("arcana", "history", "investigation", "insight"),
        saving_throws=("intelligence", "wisdom"),
        feature="magic_missile",
        feature_uses=2,
        feature_scales=True,
    ),
    "cleric": CharacterClass(
        name="Cleric",
        hit_die=8,
        priorities=(
            "wisdom",
            "constitution",
            "strength",
            "charisma",
            "dexterity",
            "intelligence",
        ),
        weapon="mace",
        base_armor=14,
        dex_cap=2,
        skills=("religion", "medicine", "insight", "persuasion"),
        saving_throws=("wisdom", "charisma"),
        feature="cure_wounds",
        feature_uses=2,
        feature_scales=True,
    ),
}
