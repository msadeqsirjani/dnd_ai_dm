import random

from utils.dice import Dice


class FixedRandom(random.Random):
    def __init__(self, value: int):
        super().__init__(0)
        self.value = value

    def randint(self, a: int, b: int) -> int:
        return max(a, min(b, self.value))


def fixed_dice(value: int) -> Dice:
    return Dice(FixedRandom(value))
