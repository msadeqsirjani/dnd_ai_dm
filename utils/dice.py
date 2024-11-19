from random import randint
from typing import List

class DiceRoller:
    @staticmethod
    def roll(dice: str) -> int:
        """Roll dice in format 'XdY' (e.g., '2d6')"""
        try:
            num_dice, sides = map(int, dice.lower().split('d'))
            return sum(randint(1, sides) for _ in range(num_dice))
        except ValueError:
            raise ValueError(f"Invalid dice format: {dice}. Use format 'XdY' (e.g., '2d6')")
    
    @staticmethod
    def roll_with_advantage() -> int:
        """Roll 2d20 and take the higher value"""
        return max(randint(1, 20), randint(1, 20))
    
    @staticmethod
    def roll_with_disadvantage() -> int:
        """Roll 2d20 and take the lower value"""
        return min(randint(1, 20), randint(1, 20))