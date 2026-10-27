from dataclasses import dataclass


@dataclass(frozen=True)
class Item:
    name: str
    price: int
    description: str
    healing: str | None = None


ITEMS = {
    "healing potion": Item(
        "Healing Potion", 50, "A red draught that knits wounds closed.", "2d4+2"
    ),
    "rations": Item("Rations", 5, "A day of dried food. Needed to camp in the wild."),
    "torch": Item("Torch", 1, "Burns for an hour and keeps the dark at bay."),
    "rope": Item("Hempen Rope", 1, "Fifty feet of sturdy rope."),
}

STARTING_GOLD = 25
STARTING_INVENTORY = {"healing potion": 2, "rations": 3, "torch": 2}
