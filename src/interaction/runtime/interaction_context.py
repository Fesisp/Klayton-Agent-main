"""
Interaction Context - Contexto de Interação Dinâmico
===================================================

Estrutura imutável com snapshot contextual derivado do WorldState, GoalRuntime e MemoryFacade.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class InteractionContext:
    """Snapshot contextual imutável para interpretação de interação."""
    active_goal_id: Optional[str] = None
    active_goal_type: Optional[str] = None

    current_map: Optional[str] = None
    current_location: Optional[str] = None

    in_battle: bool = False
    battle_enemy: Optional[str] = None

    navigation_active: bool = False
    current_task: Optional[str] = None

    last_action: Optional[str] = None
    last_outcome: Optional[str] = None

    confidence: float = 0.0
