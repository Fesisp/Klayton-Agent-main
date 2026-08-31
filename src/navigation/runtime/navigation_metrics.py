"""
Navigation Metrics - Métricas Estatísticas de Navegação
========================================================

Calcula a taxa de conclusão de rotas (Route Completion Rate) e confirmação de movimento (Movement Confirmation Rate).

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class NavigationMetrics:
    """Métricas de desempenho de navegação."""
    routes_started: int = 0
    routes_completed: int = 0
    routes_failed: int = 0

    movement_actions_sent: int = 0
    movement_actions_confirmed: int = 0

    stuck_events: int = 0
    recovery_attempts: int = 0
    recovery_successes: int = 0

    @property
    def route_completion_rate(self) -> float:
        """completed_routes / started_routes."""
        if self.routes_started == 0:
            return 0.0
        return self.routes_completed / self.routes_started

    @property
    def movement_confirmation_rate(self) -> float:
        """confirmed_progress_actions / movement_actions."""
        if self.movement_actions_sent == 0:
            return 0.0
        return self.movement_actions_confirmed / self.movement_actions_sent

    def to_dict(self) -> Dict[str, Any]:
        return {
            "routes_started": self.routes_started,
            "routes_completed": self.routes_completed,
            "routes_failed": self.routes_failed,
            "route_completion_rate": self.route_completion_rate,
            "movement_confirmation_rate": self.movement_confirmation_rate,
            "stuck_events": self.stuck_events,
            "recovery_successes": self.recovery_successes,
        }
