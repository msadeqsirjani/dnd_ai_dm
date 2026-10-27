import random
import re
from dataclasses import dataclass

_EXPRESSION = re.compile(
    r"^\s*(\d*)d(\d+)(?:(kh|kl)(\d+))?\s*([+-]\s*\d+)?\s*$", re.IGNORECASE
)
MAX_DICE = 100
MAX_SIDES = 1000


@dataclass(frozen=True)
class RollResult:
    expression: str
    rolls: tuple[int, ...]
    kept: tuple[int, ...]
    modifier: int
    total: int

    @property
    def natural(self) -> int:
        return self.kept[0]

    def __str__(self) -> str:
        modifier = f" {self.modifier:+d}" if self.modifier else ""
        return f"{self.expression}: {list(self.rolls)}{modifier} = {self.total}"


class Dice:
    def __init__(self, rng: random.Random | None = None):
        self._rng = rng or random.Random()

    def roll(self, expression: str, critical: bool = False) -> RollResult:
        match = _EXPRESSION.match(expression)
        if not match:
            raise ValueError(
                f"Invalid dice expression: {expression!r}. "
                "Use forms like 'd20', '2d6+3' or '4d6kh3'."
            )
        count_text, sides_text, keep_mode, keep_text, modifier_text = match.groups()
        count = int(count_text or 1)
        sides = int(sides_text)
        if not 1 <= count <= MAX_DICE or not 2 <= sides <= MAX_SIDES:
            raise ValueError(
                f"Dice out of range in {expression!r}: "
                f"use 1-{MAX_DICE} dice with 2-{MAX_SIDES} sides."
            )
        keep = int(keep_text) if keep_mode else count
        if not 1 <= keep <= count:
            raise ValueError(f"Cannot keep {keep} of {count} dice in {expression!r}.")
        if critical:
            count *= 2
            keep *= 2
        rolls = tuple(self._rng.randint(1, sides) for _ in range(count))
        ordered = sorted(rolls, reverse=keep_mode is None or keep_mode.lower() == "kh")
        kept = tuple(ordered[:keep]) if keep_mode else rolls
        modifier = int(modifier_text.replace(" ", "")) if modifier_text else 0
        return RollResult(
            expression.strip(), rolls, kept, modifier, sum(kept) + modifier
        )

    def d20(
        self, modifier: int = 0, advantage: bool = False, disadvantage: bool = False
    ) -> RollResult:
        if advantage == disadvantage:
            base = "1d20"
        else:
            base = "2d20kh1" if advantage else "2d20kl1"
        return self.roll(f"{base}{modifier:+d}")
