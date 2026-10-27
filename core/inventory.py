from content.items import ITEMS
from models.character import Character
from utils.dice import Dice
from utils.matching import find_match


def find_item(query: str, keys: list[str]) -> str | None:
    return find_match(query, keys, lambda key: f"{key} {ITEMS[key].name}")


def use_item(character: Character, query: str, dice: Dice) -> tuple[bool, str]:
    key = find_item(query, list(character.inventory))
    if key is None:
        return False, f"You don't have anything called '{query}'."
    item = ITEMS[key]
    if not item.healing:
        return False, f"The {item.name} has no use in a fight."
    character.remove_item(key)
    healed = character.heal(dice.roll(item.healing).total)
    return (
        True,
        f"You drink the {item.name} and regain {healed} HP. "
        f"({character.hp}/{character.max_hp} HP)",
    )
