"""
Agent Memory System - Memória em Múltiplos Níveis
===============================================

Gerencia a memória do agente em 3 camadas:
1. Working Memory (Curto prazo: posições recentes, alvos perdidos, diálogo atual)
2. Episodic Memory (Médio prazo: histórico de batalhas, XP/min por rota, vitórias/derrotas)
3. Semantic Memory (Longo prazo / permanente: Pokedex, dados de golpes, fraquezas de tipo)

Autor: Klayton Agent 2.0 Framework
Data: 2026-08-30
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
import time


@dataclass
class WorkingMemory:
    """Memória de curto prazo (segundos/minutos)."""
    last_seen_position: Optional[tuple] = None
    last_seen_time: float = 0.0
    last_dialogue_text: Optional[str] = None
    last_failed_action: Optional[str] = None
    recent_interactions: List[Dict[str, Any]] = field(default_factory=list)

    def add_interaction(self, action: str, details: Dict[str, Any]) -> None:
        self.recent_interactions.append({
            'action': action,
            'timestamp': time.time(),
            'details': details
        })
        # Mantém apenas as últimas 20 interações
        if len(self.recent_interactions) > 20:
            self.recent_interactions.pop(0)


@dataclass
class RouteEpisodicStats:
    route_name: str
    encounters_count: int = 0
    total_xp_gained: int = 0
    duration_seconds: float = 0.0

    @property
    def xp_per_minute(self) -> float:
        minutes = max(0.1, self.duration_seconds / 60.0)
        return self.total_xp_gained / minutes


@dataclass
class EpisodicMemory:
    """Memória episódica (histórico de eventos e sessões)."""
    battles_history: List[Dict[str, Any]] = field(default_factory=list)
    route_stats: Dict[str, RouteEpisodicStats] = field(default_factory=dict)

    def record_battle(self, opponent: str, victory: bool, xp_gained: int) -> None:
        self.battles_history.append({
            'opponent': opponent,
            'victory': victory,
            'xp': xp_gained,
            'timestamp': time.time()
        })


class AgentMemory:
    """
    Sistema unificado de Memória do Klayton Agent 2.0.
    """

    def __init__(self, pokemon_db: Optional[Any] = None):
        self.working: WorkingMemory = WorkingMemory()
        self.episodic: EpisodicMemory = EpisodicMemory()
        self.semantic: Optional[Any] = pokemon_db  # Referência ao PokemonDatabase legado
