"""
Goal Candidate - Representação de Candidato a Meta
==================================================

Candidato a meta emitido por necessidades internas, comandos do usuário ou eventos do ambiente.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class GoalCandidate:
    """Candidato imutável a objetivo do agente."""
    goal_type: str

    target: Optional[str] = None
    target_level: Optional[int] = None
    location_hint: Optional[str] = None

    base_priority: float = 0.5
    urgency: float = 0.0
    utility: float = 0.0

    source: str = "internal"  # user, system, need, quest, recovery, routine, memory

    interruptible: bool = True
    resumable: bool = True
