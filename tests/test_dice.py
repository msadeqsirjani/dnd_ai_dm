import random

import pytest

from tests.helpers import fixed_dice
from utils.dice import Dice


def test_roll_adds_modifier():
    result = fixed_dice(3).roll("2d6+4")
    assert result.rolls == (3, 3)
    assert result.total == 10


def test_negative_modifier_and_implicit_count():
    assert fixed_dice(5).roll("d8-2").total == 3


def test_keep_highest_drops_lowest():
    rng = random.Random(1)
    result = Dice(rng).roll("4d6kh3")
    assert len(result.kept) == 3
    assert result.total == sum(sorted(result.rolls)[1:])


def test_keep_lowest():
    result = Dice(random.Random(2)).roll("2d20kl1")
    assert result.total == min(result.rolls)


def test_critical_doubles_dice_not_modifier():
    result = fixed_dice(4).roll("1d8+3", critical=True)
    assert result.rolls == (4, 4)
    assert result.total == 11


def test_advantage_takes_higher():
    for seed in range(20):
        result = Dice(random.Random(seed)).d20(2, advantage=True)
        assert result.total == max(result.rolls) + 2


def test_advantage_and_disadvantage_cancel():
    assert len(fixed_dice(10).d20(0, advantage=True, disadvantage=True).rolls) == 1


@pytest.mark.parametrize("expression", ["", "abc", "0d6", "2d1", "3d6kh4", "1d6+"])
def test_invalid_expressions_raise(expression):
    with pytest.raises(ValueError):
        Dice().roll(expression)
