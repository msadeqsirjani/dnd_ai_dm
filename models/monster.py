from dataclasses import dataclass

from content.monsters import MONSTERS
from utils.dice import Dice


@dataclass
class Monster:
    key: str
    name: str
    max_hp: int
    hp: int
    armor_class: int
    attack_bonus: int
    damage: str
    dex_modifier: int
    xp: int

    @classmethod
    def spawn(cls, key: str, dice: Dice) -> "Monster":
        template = MONSTERS[key]
        hp = max(1, dice.roll(template.hit_points).total)
        return cls(
            key=key,
            name=template.name,
            max_hp=hp,
            hp=hp,
            armor_class=template.armor_class,
            attack_bonus=template.attack_bonus,
            damage=template.damage,
            dex_modifier=template.dex_modifier,
            xp=template.xp,
        )

    @property
    def is_alive(self) -> bool:
        return self.hp > 0

    def take_damage(self, amount: int) -> int:
        dealt = min(max(amount, 0), self.hp)
        self.hp -= dealt
        return dealt
