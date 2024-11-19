import re
from typing import Dict, List, Tuple

class TextProcessor:
    @staticmethod
    def parse_command(text: str) -> Tuple[str, List[str]]:
        """Parse user input into command and arguments"""
        words = text.lower().strip().split()
        if not words:
            return ("", [])
        return (words[0], words[1:])
    
    @staticmethod
    def extract_keywords(text: str) -> List[str]:
        """Extract important keywords from text"""
        # This could be expanded with more sophisticated NLP
        keywords = []
        important_words = ["attack", "talk", "move", "search", "inventory"]
        
        for word in text.lower().split():
            if word in important_words:
                keywords.append(word)
        
        return keywords
    
    @staticmethod
    def format_description(text: str, width: int = 80) -> str:
        """Format text for display with word wrapping"""
        words = text.split()
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + 1 <= width:
                current_line.append(word)
                current_length += len(word) + 1
            else:
                lines.append(" ".join(current_line))
                current_line = [word]
                current_length = len(word)
                
        if current_line:
            lines.append(" ".join(current_line))
            
        return "\n".join(lines)