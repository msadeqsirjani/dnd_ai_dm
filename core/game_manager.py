from typing import Optional
from models.character import Character
from models.world_state import WorldState
from core.story_generator import StoryGenerator

class GameManager:
    def __init__(self, api_key: str):
        self.story_generator = StoryGenerator(api_key)
        self.world_state = WorldState()
        self.player: Optional[Character] = None
    
    def start_new_game(self) -> str:
        # Initialize new game state
        initial_quest = self.story_generator.generate_quest("starting village", "easy")
        self.world_state.current_location = "starting village"
        return initial_quest
    
    def process_command(self, command: str) -> str:
        # Process player input and return response
        # This would be expanded to handle various commands
        return self.story_generator.generate_quest(
            self.world_state.current_location, 
            "medium"
        )