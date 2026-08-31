"""
Goal Arbitrator - Arbitrador de Prioridade de Metas
===================================================

Avalia candidatos a metas e decide qual deve estar ativa usando fórmula ponderada e margem de histerese.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

from typing import List, Optional
from .goal_candidate import GoalCandidate
from .goal_state import GoalRuntime, GoalState
from .goal_stack import GoalStack


class GoalArbitrator:
    """Arbitrador ponderado de objetivos."""

    def __init__(self, switch_margin: float = 0.15):
        self.switch_margin = switch_margin

    def calculate_score(self, candidate: GoalCandidate) -> float:
        """Calcula a pontuação de prioridade de um candidato."""
        user_bonus = 0.40 if candidate.source.lower() == "user" else 0.0
        emergency_bonus = 0.50 if "critical" in candidate.goal_type.lower() or "heal" in candidate.goal_type.lower() else 0.0

        score = candidate.base_priority + candidate.urgency + candidate.utility + user_bonus + emergency_bonus
        return score

    def select(self, candidates: List[GoalCandidate], stack: GoalStack) -> Optional[GoalRuntime]:
        """Seleciona a meta de maior pontuação respeitando a margem de histerese."""
        if not candidates:
            return stack.active()

        best_cand: Optional[GoalCandidate] = None
        best_score = -1.0

        for cand in candidates:
            sc = self.calculate_score(cand)
            if sc > best_score:
                best_score = sc
                best_cand = cand

        if best_cand is None:
            return stack.active()

        current_active = stack.active()
        if current_active and current_active.candidate:
            current_score = self.calculate_score(current_active.candidate)
            # Aplica margem de histerese se não for emergência/comando de usuário
            if best_cand.source.lower() != "user" and "critical" not in best_cand.goal_type.lower():
                if best_score < current_score + self.switch_margin:
                    return current_active

        # Cria a nova instância de runtime para o candidato vencedor
        new_runtime = GoalRuntime(candidate=best_cand)
        stack.push(new_runtime)
        return new_runtime
