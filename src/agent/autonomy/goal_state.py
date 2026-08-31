"""
Goal State & Runtime Record - Estado e Registro de Meta Ativa
============================================================

Enumeração de estados formais e classe GoalRuntime com ID imutável para rastreamento de ciclo de vida.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional
from .goal_candidate import GoalCandidate


class GoalState(Enum):
    """Estados do ciclo de vida de um objetivo."""
    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class GoalRuntime:
    """Registro runtime de uma meta ativa com suporte a serialização."""
    id: str = field(default_factory=lambda: uuid.uuid4().hex)
    candidate: Optional[GoalCandidate] = None

    state: GoalState = GoalState.PENDING

    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None

    progress: float = 0.0

    attempts: int = 0
    replans: int = 0

    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "goal_type": self.candidate.goal_type if self.candidate else "UNKNOWN",
            "target": self.candidate.target if self.candidate else None,
            "target_level": self.candidate.target_level if self.candidate else None,
            "state": self.state.value,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "progress": self.progress,
            "attempts": self.attempts,
            "replans": self.replans,
            "metadata": self.metadata,
        }
