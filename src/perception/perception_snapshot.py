"""
Perception Snapshot DTO - Objeto Único de Transferência da Percepção Visual/OCR
================================================================================

Isola a camada de visão computacional, OCR e detectores do modelo cognitivo do Agente.
Todas as saídas das capturas são empacotadas em um PerceptionSnapshot antes de atualizar
o WorldState.

Autor: Klayton Companion Agent Framework
Data: 2026-08-30
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
import time
from ..world.world_state import PokemonInfo, BattleState, ResourcesState, QuestState


@dataclass
class PerceptionSnapshot:
    """DTO imutável e estruturado contendo o estado detectado no frame atual."""
    game_state: str = "EXPLORING"
    current_map: str = "Unknown"
    player_position: Optional[Tuple[int, int]] = None
    team: List[PokemonInfo] = field(default_factory=list)
    battle: Optional[BattleState] = None
    resources: Optional[ResourcesState] = None
    nearby_players: List[Dict[str, Any]] = field(default_factory=list)
    dialog: Dict[str, Any] = field(default_factory=dict)
    quest: Optional[QuestState] = None
    confidence: float = 1.0
    timestamp: float = field(default_factory=time.time)
