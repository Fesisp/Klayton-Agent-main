"""
Battle Decision - Decisão Estruturada da Estratégia de Combate
==============================================================

Representa a decisão tática avaliada pela BattleStrategy contendo ação, pontuação, confiança e justificativa.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

from dataclasses import dataclass
from .battle_action import BattleAction


@dataclass(frozen=True)
class BattleDecision:
    """Decisão ponderada emitida pelo motor tático de batalha."""
    action: BattleAction
    score: float
    confidence: float
    reason: str
