"""
Relationship Context - Modelo de Relacionamento Social
======================================================

Rastreia o contexto social e a relação dinâmica entre o Klayton e o jogador humano (liderança, distância, instruções ativas e estado de espera).

Autor: Klayton Companion Agent
Data: 2026-08-30
"""

from dataclasses import dataclass, field
from typing import Optional
import time


@dataclass
class RelationshipState:
    """Estado do relacionamento social com o jogador humano."""
    leader_name: str = "Felipe"
    distance_tiles: float = 0.0
    last_known_direction: Optional[str] = None
    shared_goal: Optional[str] = None
    last_instruction: Optional[str] = None  # ex: "me espera aqui", "vem comigo"
    is_waiting_for_player: bool = False
    is_player_in_battle: bool = False
    last_interaction_time: float = field(default_factory=time.time)

    def set_instruction(self, instruction: str) -> None:
        self.last_instruction = instruction
        self.last_interaction_time = time.time()
        
        instruction_lower = instruction.lower()
        if "espera" in instruction_lower or "fica ai" in instruction_lower:
            self.is_waiting_for_player = True
        elif "vem" in instruction_lower or "segue" in instruction_lower:
            self.is_waiting_for_player = False

    def update_distance(self, distance_tiles: float) -> None:
        self.distance_tiles = distance_tiles
        # Se o jogador se aproximar enquanto o agente estava esperando, retoma a atividade compartilhada
        if self.is_waiting_for_player and distance_tiles <= 3.0:
            self.is_waiting_for_player = False
