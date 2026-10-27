from dataclasses import dataclass
from typing import Protocol

from utils.dice import Dice, RollResult


class Target(Protocol):
    name: str

    @property
    def armor_class(self) -> int: ...

    def take_damage(self, amount: int) -> int: ...


@dataclass(frozen=True)
class AttackResult:
    hit: bool
    critical: bool
    damage: int
    roll: RollResult


def resolve_attack(
    dice: Dice,
    bonus: int,
    damage: str,
    target: Target,
    advantage: bool = False,
    disadvantage: bool = False,
    extra_damage: str | None = None,
) -> AttackResult:
    roll = dice.d20(bonus, advantage, disadvantage)
    critical = roll.natural == 20
    hit = critical or (roll.natural != 1 and roll.total >= target.armor_class)
    if not hit:
        return AttackResult(False, False, 0, roll)
    total = dice.roll(damage, critical=critical).total
    if extra_damage:
        total += dice.roll(extra_damage, critical=critical).total
    return AttackResult(True, critical, target.take_damage(max(1, total)), roll)


def describe_attack(attacker: str, target: Target, result: AttackResult) -> str:
    versus = f"({result.roll.total} vs AC {target.armor_class})"
    if not result.hit:
        fumble = " A clumsy miss!" if result.roll.natural == 1 else ""
        return f"{attacker} attacks {target.name} {versus} and misses.{fumble}"
    critical = " Critical hit!" if result.critical else ""
    return (
        f"{attacker} hits {target.name} {versus} for {result.damage} damage.{critical}"
    )
