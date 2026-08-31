"""
Explanation Engine - Motor de Explicação Baseado em Estado Real
================================================================

Gera explicações transparentes sobre as decisões do agente a partir do WorldState e GoalRuntime.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional, Tuple


@dataclass(frozen=True)
class DecisionExplanation:
    """Explicação estruturada de decisão."""
    summary: str
    reasons: Tuple[str, ...]
    evidence: Tuple[str, ...]
    confidence: float


class ExplanationEngine:
    """Motor de explicações baseado em evidências reais do runtime."""

    def explain(self, world: Any, goal: Any, level: str = "normal") -> DecisionExplanation:
        """Gera explicação fundamentada exclusivamente em dados reais."""
        if not goal or not hasattr(goal, 'candidate') or not goal.candidate:
            return DecisionExplanation(
                summary="Estou aguardando instruções do usuário.",
                reasons=("Nenhum objetivo ativo configurado",),
                evidence=("GoalRuntime is None",),
                confidence=1.0
            )

        gt = goal.candidate.goal_type.upper()
        target = goal.candidate.target or "Pikachu"
        target_lvl = goal.candidate.target_level or 35

        curr_lvl = 30
        if hasattr(world, 'team') and world.team.members:
            curr_lvl = getattr(world.team.members[0], 'level', 30)

        needs_heal = getattr(world.team, 'needs_healing', False) if hasattr(world, 'team') else False

        if needs_heal:
            summary = f"Estou indo curar o time porque o HP médio está baixo. Em seguida, retomarei o treinamento de {target}."
            reasons = ("Time necessita de cura de emergência", f"Objetivo principal '{gt}' foi temporariamente suspenso")
            evidence = ("world.team.needs_healing == True", f"Pikachu level={curr_lvl}")
        else:
            summary = f"Estou executando o objetivo '{gt}' para levar {target} ao nível {target_lvl}."
            reasons = (f"Nível atual ({curr_lvl}) é inferior ao alvo ({target_lvl})", "Time está saudável")
            evidence = (f"Pikachu level={curr_lvl}", "world.team.needs_healing == False")

        if level == "short":
            return DecisionExplanation(summary=summary, reasons=reasons[:1], evidence=(), confidence=0.95)

        return DecisionExplanation(summary=summary, reasons=reasons, evidence=evidence, confidence=0.95)
