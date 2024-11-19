from dataclasses import dataclass, field
from typing import Dict, List, Set
from models.npc import NPC

@dataclass
class Location:
    name: str
    description: str
    connected_locations: Set[str]
    npcs: List[str]  # NPC names present at this location
    items: List[str]  # Items available at this location

@dataclass
class WorldState:
    current_location: str = "starting_village"
    time_of_day: int = 0  # 0-23 hours
    weather: str = "clear"
    active_quests: List[str] = field(default_factory=list)
    completed_quests: List[str] = field(default_factory=list)
    locations: Dict[str, Location] = field(default_factory=dict)
    global_state: Dict[str, bool] = field(default_factory=dict)
    
    def advance_time(self, hours: int) -> None:
        """Advance world time by specified hours"""
        self.time_of_day = (self.time_of_day + hours) % 24
    
    def add_location(self, location: Location) -> None:
        """Add a new location to the world"""
        self.locations[location.name] = location
    
    def can_travel_to(self, destination: str) -> bool:
        """Check if player can travel to destination from current location"""
        return (destination in 
                self.locations[self.current_location].connected_locations)