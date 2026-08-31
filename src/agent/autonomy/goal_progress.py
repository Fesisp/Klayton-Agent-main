"""
Goal Progress - Dataclass de Avaliação de Progresso de Meta
============================================================

Contém a fração de avanço empírico, se houve progresso, se está bloqueada ou concluída.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GoalProgress:
    """Resultado da avaliação empírica do avanço de uma meta."""
    fraction: float

    advanced: bool
    blocked: bool
    complete: bool

    reason: str
