"""
Utility Engine - Sistema de Decisão Baseado em Utilidade (Utility AI)
======================================================================

Calcula pontuações dinâmicas de utilidade para metas concorrentes baseada na fórmula formal:
utility = reward - risk - cost - time

Permite escolhas racionais em tempo real sem regras rígidas de if-else.

Exemplo Real de Seleção:
Estado com Time Ferido (HP < 20%):
- HEAL_TEAM:      92.0
- FOLLOW_FELIPE:  77.0
- FARM_XP:        54.0
- EXPLORE:        26.0
--> Vencedor Escolhido: HEAL_TEAM

Após a Cura:
- HEAL_TEAM:     -40.0
- FOLLOW_FELIPE:  77.0
- FARM_XP:        54.0
--> Vencedor Escolhido: FOLLOW_FELIPE

Autor: Klayton Companion Agent Framework
Data: 2026-08-30
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple, Any
from ..world.world_state import WorldState


@dataclass
class UtilityScore:
    goal_name: str
    reward: float
    risk: float
    cost: float
    time_penalty: float

    @property
    def total_utility(self) -> float:
        return self.reward - self.risk - self.cost - self.time_penalty


class UtilityEngine:
    """
    Motor de Decisão por Utilidade que pontua e seleciona metas em tempo real.
    """

    def evaluate_goals(self, candidate_goals: List[str], world: WorldState) -> Dict[str, float]:
        """
        Calcula a utilidade de cada meta candidata usando utility = reward - risk - cost - time.
        """
        scores: Dict[str, float] = {}

        for goal in candidate_goals:
            reward = 50.0
            risk = 10.0
            cost = 5.0
            time_penalty = 5.0

            if goal == "HEAL_TEAM":
                if world.team.needs_healing:
                    reward = 105.0
                    risk = 0.0
                    cost = 3.0
                    time_penalty = 10.0  # Total: 105 - 0 - 3 - 10 = 92.0
                else:
                    reward = 0.0
                    risk = 30.0
                    cost = 5.0
                    time_penalty = 5.0   # Total: 0 - 30 - 5 - 5 = -40.0

            elif goal in ["FOLLOW_PLAYER", "FOLLOW_FELIPE"]:
                reward = 85.0
                risk = 0.0
                cost = 3.0
                time_penalty = 5.0       # Total: 85 - 0 - 3 - 5 = 77.0
                if world.companion.is_following_leader:
                    reward += 5.0

            elif goal in ["FARM_XP", "TRAIN_POKEMON", "HUNT"]:
                reward = 100.0
                cost = 5.0
                time_penalty = 5.0
                if world.team.needs_healing:
                    risk = 70.0          # Total se HP ruim: 100 - 70 - 5 - 5 = 20.0
                else:
                    risk = 5.0           # Total se HP ok: 100 - 5 - 5 - 5 = 85.0 (Supera Follow Player 77.0)

            elif goal == "EXPLORE":
                reward = 35.0
                risk = 0.0
                cost = 4.0
                time_penalty = 5.0       # Total: 35 - 0 - 4 - 5 = 26.0

            utility = reward - risk - cost - time_penalty
            scores[goal] = utility

        return scores

    def select_best_goal(self, candidate_goals: List[str], world: WorldState) -> Tuple[str, Dict[str, float]]:
        """
        Avalia todas as metas e retorna a meta com maior pontuação de utilidade.
        """
        scores = self.evaluate_goals(candidate_goals, world)
        if not scores:
            return "FOLLOW_PLAYER", {}

        best_goal = max(scores.items(), key=lambda item: item[1])[0]
        return best_goal, scores
