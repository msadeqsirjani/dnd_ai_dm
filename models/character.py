from dataclasses import asdict, dataclass, field

from content.heroes import CLASSES, RACES, WEAPONS, CharacterClass, Race, Weapon
from content.rules import (
    MAX_LEVEL,
    SKILLS,
    XP_THRESHOLDS,
    ability_modifier,
    level_for_xp,
    proficiency_bonus,
)


@dataclass
class Character:
    name: str
    race: str
    character_class: str
    abilities: dict[str, int]
    level: int = 1
    xp: int = 0
    max_hp: int = 1
    hp: int = 1
    gold: int = 0
    inventory: dict[str, int] = field(default_factory=dict)
    feature_uses: int = 0

    @property
    def race_info(self) -> Race:
        return RACES[self.race]

    @property
    def class_info(self) -> CharacterClass:
        return CLASSES[self.character_class]

    @property
    def weapon(self) -> Weapon:
        return WEAPONS[self.class_info.weapon]

    @property
    def is_alive(self) -> bool:
        return self.hp > 0

    @property
    def proficiency(self) -> int:
        return proficiency_bonus(self.level)

    def modifier(self, ability: str) -> int:
        return ability_modifier(self.abilities[ability])

    @property
    def armor_class(self) -> int:
        dex_bonus = self.modifier("dexterity")
        cap = self.class_info.dex_cap
        if cap is not None:
            dex_bonus = min(dex_bonus, cap)
        return self.class_info.base_armor + dex_bonus

    @property
    def attack_ability(self) -> str:
        if self.weapon.ability == "finesse":
            return max(("strength", "dexterity"), key=self.modifier)
        return self.weapon.ability

    @property
    def attack_bonus(self) -> int:
        return self.modifier(self.attack_ability) + self.proficiency

    @property
    def damage(self) -> str:
        return f"{self.weapon.damage}{self.modifier(self.attack_ability):+d}"

    def skill_bonus(self, skill: str) -> int:
        bonus = self.modifier(SKILLS[skill])
        if skill in self.class_info.skills:
            bonus += self.proficiency
        return bonus

    def saving_throw_bonus(self, ability: str) -> int:
        bonus = self.modifier(ability)
        if ability in self.class_info.saving_throws:
            bonus += self.proficiency
        return bonus

    @property
    def max_feature_uses(self) -> int:
        scaling = self.level // 2 if self.class_info.feature_scales else 0
        return self.class_info.feature_uses + scaling

    @property
    def xp_to_next(self) -> int | None:
        return XP_THRESHOLDS[self.level] if self.level < MAX_LEVEL else None

    def take_damage(self, amount: int) -> int:
        dealt = min(max(amount, 0), self.hp)
        self.hp -= dealt
        return dealt

    def heal(self, amount: int) -> int:
        healed = min(max(amount, 0), self.max_hp - self.hp)
        self.hp += healed
        return healed

    def gain_xp(self, amount: int) -> list[int]:
        self.xp += amount
        new_levels = []
        while self.level < min(level_for_xp(self.xp), MAX_LEVEL):
            self.level += 1
            increase = max(
                1, self.class_info.hit_die // 2 + 1 + self.modifier("constitution")
            )
            self.max_hp += increase
            self.hp += increase
            new_levels.append(self.level)
        return new_levels

    def long_rest(self) -> None:
        self.hp = self.max_hp
        self.feature_uses = self.max_feature_uses

    def add_item(self, key: str, quantity: int = 1) -> None:
        self.inventory[key] = self.inventory.get(key, 0) + quantity

    def remove_item(self, key: str, quantity: int = 1) -> bool:
        if self.inventory.get(key, 0) < quantity:
            return False
        self.inventory[key] -= quantity
        if not self.inventory[key]:
            del self.inventory[key]
        return True

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Character":
        return cls(**data)
