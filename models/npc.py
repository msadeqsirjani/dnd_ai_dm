from dataclasses import dataclass
from typing import Dict, List
from enum import Enum

class Alignment(Enum):
    LAWFUL_GOOD = "Lawful Good"
    NEUTRAL_GOOD = "Neutral Good"
    CHAOTIC_GOOD = "Chaotic Good"
    LAWFUL_NEUTRAL = "Lawful Neutral"
    TRUE_NEUTRAL = "True Neutral"
    CHAOTIC_NEUTRAL = "Chaotic Neutral"
    LAWFUL_EVIL = "Lawful Evil"
    NEUTRAL_EVIL = "Neutral Evil"
    CHAOTIC_EVIL = "Chaotic Evil"

@dataclass
class NPC:
    name: str
    race: str
    occupation: str
    alignment: Alignment
    stats: Dict[str, int]
    disposition: int  # 0-100, how friendly they are to the player
    knowledge: List[str]  # List of topics/secrets this NPC knows
    location: str
    
    def modify_disposition(self, amount: int) -> None:
        """Modify NPC's disposition towards player"""
        self.disposition = max(0, min(100, self.disposition + amount))
    
    def will_share_info(self, topic: str) -> bool:
        """Determine if NPC will share specific information"""
        if topic not in self.knowledge:
            return False
        # Higher disposition means more likely to share
        return (self.disposition > 50)