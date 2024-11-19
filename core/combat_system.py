from typing import List, Tuple
from models.character import Character
from models.npc import NPC
from utils.dice import DiceRoller

class CombatSystem:
    def __init__(self):
        self.initiative_order: List[Tuple[int, str, bool]] = []  # (initiative, name, is_player)
        self.current_turn: int = 0
    
    def start_combat(self, player: Character, enemies: List[NPC]) -> str:
        """Initialize combat and roll initiative"""
        self.initiative_order.clear()
        
        # Roll player initiative
        player_init = DiceRoller.roll("1d20") + self._get_modifier(player.stats["dexterity"])
        self.initiative_order.append((player_init, player.name, True))
        
        # Roll enemy initiatives
        for enemy in enemies:
            enemy_init = DiceRoller.roll("1d20") + self._get_modifier(enemy.stats["dexterity"])
            self.initiative_order.append((enemy_init, enemy.name, False))
        
        # Sort by initiative (highest first)
        self.initiative_order.sort(reverse=True)
        self.current_turn = 0
        
        return self._format_initiative_order()
    
    def _get_modifier(self, stat: int) -> int:
        """Calculate ability modifier from stat"""
        return (stat - 10) // 2
    
    def process_attack(self, attacker: Character | NPC, 
                      defender: Character | NPC) -> str:
        """Process an attack action"""
        attack_roll = DiceRoller.roll("1d20")
        attack_bonus = self._get_modifier(attacker.stats["strength"])
        
        # Calculate if hit
        if attack_roll + attack_bonus >= defender.stats.get("armor_class", 10):
            # Roll damage
            damage = DiceRoller.roll("1d8") + attack_bonus
            defender.modify_hp(-damage)
            return f"{attacker.name} hits {defender.name} for {damage} damage!"
        
        return f"{attacker.name} misses {defender.name}!"
    
    def _format_initiative_order(self) -> str:
        """Format initiative order for display"""
        return "\n".join(
            f"{init}: {name} {'(Player)' if is_player else '(Enemy)'}"
            for init, name, is_player in self.initiative_order
        )