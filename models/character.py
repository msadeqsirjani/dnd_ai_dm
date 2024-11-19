from dataclasses import dataclass
from typing import Dict, List

@dataclass
class Character:
    name: str
    level: int
    stats: Dict[str, int]  # strength, dexterity, etc.
    hp: int
    max_hp: int
    inventory: List[str]
    
    def modify_hp(self, amount: int) -> None:
        self.hp = min(max(0, self.hp + amount), self.max_hp)
    
    def add_item(self, item: str) -> None:
        self.inventory.append(item)