"""
Autonomy Policy - Políticas de Tentativas e Replano
===================================================

Define limites de tentativas por tarefa, limite de replanejamentos e limites de tempo.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class RetryPolicy:
    """Política imutável de limites de re-tentativa e recuperação."""
    max_task_attempts: int = 3
    max_goal_replans: int = 5
    max_goal_runtime_seconds: Optional[float] = 3600.0
