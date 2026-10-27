from content.items import ITEMS
from content.rules import ABILITIES, skill_label
from core.class_features import feature_of
from models.character import Character


def character_sheet(character: Character) -> list[str]:
    cls = character.class_info
    feature = feature_of(character)
    next_level = character.xp_to_next
    progress = f" / {next_level}" if next_level else " (max level)"
    abilities = "  ".join(
        f"{ability[:3].upper()} {character.abilities[ability]} "
        f"({character.modifier(ability):+d})"
        for ability in ABILITIES
    )
    skills = ", ".join(
        f"{skill_label(skill)} {character.skill_bonus(skill):+d}"
        for skill in cls.skills
    )
    return [
        f"== {character.name} ==",
        f"Level {character.level} {character.race_info.name} {cls.name}. "
        f"XP {character.xp}{progress}.",
        f"HP {character.hp}/{character.max_hp}. AC {character.armor_class}. "
        f"Proficiency +{character.proficiency}.",
        f"  {abilities}",
        f"Weapon: {character.weapon.name} ({character.attack_bonus:+d} to hit, "
        f"{character.damage} damage).",
        f"Proficient skills: {skills}.",
        f"Feature: {feature.name} ({character.feature_uses}/"
        f"{character.max_feature_uses} uses). {feature.description}",
    ]


def inventory_lines(character: Character) -> list[str]:
    lines = [f"Gold: {character.gold}"]
    if not character.inventory:
        return lines + ["Your pack is empty."]
    return lines + [
        f"  {quantity} x {ITEMS[key].name}: {ITEMS[key].description}"
        for key, quantity in sorted(character.inventory.items())
    ]
