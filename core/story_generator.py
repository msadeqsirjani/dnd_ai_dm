from typing import List, Dict
import random
from openai import OpenAI

class StoryGenerator:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.story_context = []
        
    def generate_quest(self, location: str, difficulty: str) -> str:
        prompt = f"Generate a D&D quest in {location} with {difficulty} difficulty."
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a D&D Dungeon Master."},
                {"role": "user", "content": prompt}
            ]
        )
        
        return response.choices[0].message.content