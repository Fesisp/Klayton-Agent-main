"""
Navigation Executor - Executor Físico de Movimento
===================================================

Traduz uma NavigationAction em comando físico sem considerar o envio como sucesso definitivo.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Optional
from .navigation_action import NavigationAction, NavigationActionType
from .navigation_observation import NavigationObservation


class NavigationExecutorPhase(Enum):
    """Fases da execução física de movimento."""
    IDLE = "idle"
    INPUT_SENT = "input_sent"
    WAITING_OBSERVATION = "waiting_observation"
    VERIFYING = "verifying"
    DONE = "done"
    FAILED = "failed"


class NavigationExecutor:
    """Executor físico de comandos de navegação."""

    def __init__(self):
        self.phase: NavigationExecutorPhase = NavigationExecutorPhase.IDLE
        self.current_action: Optional[NavigationAction] = None

    def start(self, action: NavigationAction) -> None:
        self.current_action = action
        self.phase = NavigationExecutorPhase.INPUT_SENT

    def tick(self, input_simulator: Any, observation: Optional[NavigationObservation] = None) -> NavigationExecutorPhase:
        if not self.current_action or self.phase == NavigationExecutorPhase.DONE:
            return NavigationExecutorPhase.DONE

        if self.phase == NavigationExecutorPhase.INPUT_SENT:
            action = self.current_action
            try:
                if action.type == NavigationActionType.MOVE and action.direction:
                    dir_lower = action.direction.lower()
                    if hasattr(input_simulator, 'press'):
                        input_simulator.press(dir_lower)
                    elif hasattr(input_simulator, 'move'):
                        input_simulator.move(dir_lower)

                self.phase = NavigationExecutorPhase.WAITING_OBSERVATION
            except Exception:
                self.phase = NavigationExecutorPhase.FAILED

        return self.phase

    def reset(self) -> None:
        self.phase = NavigationExecutorPhase.IDLE
        self.current_action = None
