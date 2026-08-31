"""
Battle Metrics - Cálculo de Confiabilidade de Combate
======================================================

Calcula a taxa de confirmação de ações (Action Confirmation Rate) e estatísticas de runtime.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class BattleMetrics:
    """Calculador de métricas estatísticas de combate."""
    actions_total: int = 0
    actions_confirmed: int = 0
    actions_rejected: int = 0
    actions_timeout: int = 0
    actions_ambiguous: int = 0

    @property
    def action_confirmation_rate(self) -> float:
        """Fórmula soberana: confirmed_actions / executed_actions."""
        if self.actions_total == 0:
            return 0.0
        return self.actions_confirmed / self.actions_total

    def record_action(self, status_str: str) -> None:
        """Registra o resultado de uma ação."""
        self.actions_total += 1
        st = status_str.lower()
        if "confirmed" in st:
            self.actions_confirmed += 1
        elif "rejected" in st:
            self.actions_rejected += 1
        elif "timeout" in st:
            self.actions_timeout += 1
        else:
            self.actions_ambiguous += 1

    def to_dict(self) -> Dict[str, Any]:
        return {
            "actions_total": self.actions_total,
            "actions_confirmed": self.actions_confirmed,
            "actions_rejected": self.actions_rejected,
            "actions_timeout": self.actions_timeout,
            "actions_ambiguous": self.actions_ambiguous,
            "action_confirmation_rate": self.action_confirmation_rate,
        }
