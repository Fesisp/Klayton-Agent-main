"""
Supervision Gate - Portão de Decisão de Supervisão Humana
==========================================================

Avalia a confiança do WorldState, foco de janela e saúde do runtime, emitindo decisões ALLOW, PAUSE ou BLOCK.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Optional
from .compliance_policy import CompliancePolicy


class SupervisionDecision(Enum):
    ALLOW = "allow"
    PAUSE = "pause"
    BLOCK = "block"


class SupervisionGate:
    """Portão de avaliação de supervisão e segurança."""

    def __init__(self, policy: Optional[CompliancePolicy] = None):
        self.policy = policy or CompliancePolicy()

    def evaluate(self, world_confidence: float = 1.0, window_focused: bool = True, runtime_healthy: bool = True) -> SupervisionDecision:
        """Avalia as condições do ambiente e retorna a decisão de supervisão."""
        if not window_focused and self.policy.require_correct_window_focus:
            return SupervisionDecision.BLOCK

        if not runtime_healthy:
            return SupervisionDecision.PAUSE

        if self.policy.pause_on_low_confidence and world_confidence < self.policy.minimum_world_confidence:
            return SupervisionDecision.PAUSE

        return SupervisionDecision.ALLOW
