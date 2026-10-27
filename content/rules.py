ABILITIES = (
    "strength",
    "dexterity",
    "constitution",
    "intelligence",
    "wisdom",
    "charisma",
)

SKILLS = {
    "athletics": "strength",
    "acrobatics": "dexterity",
    "sleight_of_hand": "dexterity",
    "stealth": "dexterity",
    "arcana": "intelligence",
    "history": "intelligence",
    "investigation": "intelligence",
    "nature": "intelligence",
    "religion": "intelligence",
    "animal_handling": "wisdom",
    "insight": "wisdom",
    "medicine": "wisdom",
    "perception": "wisdom",
    "survival": "wisdom",
    "deception": "charisma",
    "intimidation": "charisma",
    "performance": "charisma",
    "persuasion": "charisma",
}

XP_THRESHOLDS = (0, 300, 900, 2700, 6500, 14000, 23000, 34000, 48000, 64000)
MAX_LEVEL = len(XP_THRESHOLDS)
STANDARD_ARRAY = (15, 14, 13, 12, 10, 8)


def ability_modifier(score: int) -> int:
    return (score - 10) // 2


def proficiency_bonus(level: int) -> int:
    return 2 + (level - 1) // 4


def level_for_xp(xp: int) -> int:
    return sum(1 for threshold in XP_THRESHOLDS if xp >= threshold)


def skill_label(skill: str) -> str:
    return skill.replace("_", " ").title()
