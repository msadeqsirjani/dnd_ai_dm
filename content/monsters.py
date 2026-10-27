from dataclasses import dataclass


@dataclass(frozen=True)
class MonsterTemplate:
    name: str
    hit_points: str
    armor_class: int
    attack_bonus: int
    damage: str
    dex_modifier: int
    xp: int
    tier: int


MONSTERS = {
    "giant rat": MonsterTemplate("Giant Rat", "2d6", 12, 4, "1d4+2", 2, 25, 1),
    "bandit": MonsterTemplate("Bandit", "2d8+2", 12, 3, "1d6+1", 1, 25, 1),
    "wolf": MonsterTemplate("Wolf", "2d8+2", 13, 4, "2d4+2", 2, 50, 1),
    "goblin": MonsterTemplate("Goblin", "2d6", 15, 4, "1d6+2", 2, 50, 1),
    "skeleton": MonsterTemplate("Skeleton", "2d8+4", 13, 4, "1d6+2", 2, 50, 1),
    "orc": MonsterTemplate("Orc", "2d8+6", 13, 5, "1d12+3", 1, 100, 2),
    "giant spider": MonsterTemplate(
        "Giant Spider", "4d10+4", 14, 5, "1d8+3", 3, 200, 2
    ),
    "ogre": MonsterTemplate("Ogre", "7d10+21", 11, 6, "2d8+4", -1, 450, 3),
}
