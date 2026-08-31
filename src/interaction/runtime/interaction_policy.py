"""
Interaction Policy - Política de Precedência e Confirmações
==========================================================

Define limites de confiança para execução automática e precedência:
safety > explicit user command > persistent user preference > autonomy policy

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class InteractionPolicy:
    """Política imutável de limites de interação."""
    command_min_confidence: float = 0.75
    critical_command_min_confidence: float = 0.90

    def allow_execution(self, confidence: float, is_critical: bool = False) -> bool:
        if is_critical:
            return confidence >= self.critical_command_min_confidence
        return confidence >= self.command_min_confidence
