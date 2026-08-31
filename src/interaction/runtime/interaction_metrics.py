"""
Interaction Metrics - Métricas Estatísticas de Interação Humana
================================================================

Calcula a taxa de resolução de comandos (Command Resolution Rate) e estatísticas de ambiguidade.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class InteractionMetrics:
    """Calculador de métricas de interação social."""
    commands_received: int = 0
    commands_resolved: int = 0
    commands_ambiguous: int = 0

    clarifications_requested: int = 0
    clarifications_resolved: int = 0

    user_corrections: int = 0
    teachings_received: int = 0

    npc_interactions: int = 0
    npc_interactions_confirmed: int = 0
    explanations_requested: int = 0

    @property
    def command_resolution_rate(self) -> float:
        """commands_resolved / commands_received."""
        if self.commands_received == 0:
            return 0.0
        return self.commands_resolved / self.commands_received

    def to_dict(self) -> Dict[str, Any]:
        return {
            "commands_received": self.commands_received,
            "commands_resolved": self.commands_resolved,
            "command_resolution_rate": self.command_resolution_rate,
            "commands_ambiguous": self.commands_ambiguous,
            "clarifications_requested": self.clarifications_requested,
            "user_corrections": self.user_corrections,
            "teachings_received": self.teachings_received,
            "explanations_requested": self.explanations_requested,
        }
