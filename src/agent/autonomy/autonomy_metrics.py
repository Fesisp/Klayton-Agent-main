"""
Autonomy Metrics - Cálculo de Confiabilidade e Métricas de Autonomia
=====================================================================

Calcula a taxa de conclusão de metas (Goal Completion Rate) e estatísticas de replanejamento.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class AutonomyMetrics:
    """Métricas de autonomia e planejamento de longo alcance."""
    goals_created: int = 0
    goals_completed: int = 0
    goals_failed: int = 0
    goals_cancelled: int = 0

    tasks_completed: int = 0
    tasks_failed: int = 0

    goal_replans: int = 0
    goal_interruptions: int = 0
    loops_detected: int = 0

    @property
    def goal_completion_rate(self) -> float:
        """completed / terminal_goals."""
        terminal = self.goals_completed + self.goals_failed + self.goals_cancelled
        if terminal == 0:
            return 0.0
        return self.goals_completed / terminal

    def to_dict(self) -> Dict[str, Any]:
        return {
            "goals_created": self.goals_created,
            "goals_completed": self.goals_completed,
            "goals_failed": self.goals_failed,
            "goals_cancelled": self.goals_cancelled,
            "goal_completion_rate": self.goal_completion_rate,
            "tasks_completed": self.tasks_completed,
            "goal_replans": self.goal_replans,
            "loops_detected": self.loops_detected,
        }
