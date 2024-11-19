from core.game_manager import GameManager
from dotenv import load_dotenv
import os

def main():
    # Load environment variables from .env file
    load_dotenv()
    
    # Get API key from loaded environment variables
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY not found in .env file")
        return
    
    game = GameManager(api_key)
    
    print("Welcome to AI D&D!")
    print("=================")
    
    # Start new game
    initial_quest = game.start_new_game()
    print("\nYour quest begins:")
    print(initial_quest)
    
    # Main game loop
    while True:
        command = input("\nWhat would you like to do? (or 'quit' to exit): ")
        
        if command.lower() == 'quit':
            break
            
        response = game.process_command(command)
        print("\n" + response)

if __name__ == "__main__":
    main()