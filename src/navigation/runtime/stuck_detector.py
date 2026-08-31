"""
Stuck Detector - Detecção e Classificação de Bloqueio Espacial
=============================================================

Rastreia falhas consecutivas de progresso e atribui a severidade do bloqueio (SUSPECTED, CONFIRMED, HARD).

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

from enum import Enum
from typing import Optional
from .navigation_progress import NavigationProgress


class StuckSeverity(Enum):
    """Níveis de severidade do travamento/stuck."""
    NONE = "none"
    SUSPECTED = "suspected"
    CONFIRMED = "confirmed"
    HARD = "hard"


class StuckDetector:
    """Detector de bloqueio espacial."""

    def __init__(self, repeated_action_limit: int = 4, hard_stuck_limit: int = 8):
        self.repeated_action_limit = repeated_action_limit
        self.hard_stuck_limit = hard_stuck_limit
        self.no_progress_count: int = 0

    def update(self, progress: NavigationProgress) -> StuckSeverity:
        """Atualiza o contador com o progresso verificado e retorna a severidade."""
        if progress == NavigationProgress.NO_PROGRESS:
            self.no_progress_count += 1
        elif progress in [NavigationProgress.PROGRESS, NavigationProgress.WAYPOINT_REACHED, NavigationProgress.MAP_CHANGED, NavigationProgress.ARRIVED]:
            self.no_progress_count = 0
            return StuckSeverity.NONE

        if self.no_progress_count >= self.hard_stuck_limit:
            return StuckSeverity.HARD
        elif self.no_progress_count >= self.repeated_action_limit:
            return StuckSeverity.CONFIRMED
        elif self.no_progress_count >= 2:
            return StuckSeverity.SUSPECTED

        return StuckSeverity.NONE

    def reset(self) -> None:
        self.no_progress_count = 0
