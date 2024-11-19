from typing import Dict, List, Optional
from models.npc import NPC, Alignment
from utils.dice import DiceRoller
import random
import json

class NPCManager:
    def __init__(self):
        self.npcs: Dict[str, NPC] = {}
        self.name_templates = self._load_name_templates()
    
    def _load_name_templates(self) -> Dict:
        # In practice, load from a JSON file
        return {
            "human": {
                "first": ["John", "Mary", "Robert", "Emma"],
                "last": ["Smith", "Johnson", "Williams"]
            }
            # Add more races...
        }
    
    def generate_npc(self, location: str) -> NPC:
        """Generate a random NPC for a given location"""
        race = random.choice(["human", "elf", "dwarf"])
        first_name = random.choice(self.name_templates[race]["first"])
        last_name = random.choice(self.name_templates[race]["last"])
        
        return NPC(
            name=f"{first_name} {last_name}",
            race=race,
            occupation=random.choice(["merchant", "guard", "farmer", "innkeeper"]),
            alignment=random.choice(list(Alignment)),
            stats={
                "strength": DiceRoller.roll("3d6"),
                "dexterity": DiceRoller.roll("3d6"),
                "constitution": DiceRoller.roll("3d6"),
                "intelligence": DiceRoller.roll("3d6"),
                "wisdom": DiceRoller.roll("3d6"),
                "charisma": DiceRoller.roll("3d6")
            },
            disposition=random.randint(30, 70),
            knowledge=[],
            location=location
        )
    
    def get_npc(self, name: str) -> Optional[NPC]:
        """Retrieve an NPC by name"""
        return self.npcs.get(name)