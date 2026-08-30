"""
Utility Engine - Sistema de Decisão Baseado em Utilidade (Utility AI)
======================================================================

Calcula a pontuação de utilidade de ações/metas baseada na fórmula:
utility = reward - risk - cost - time

Permite escolhas racionais em cenários de incerteza ou múltiplas escolhas.

Autor: Klayton Agent 2.0 Framework
Data: 2026-08-30
"""

from dataclasses import dataclass
from typing import Dict, Any
from ..world.world_state import WorldState


@dataclass
class UtilityScore:
    action_name: str
    reward: float
    risk: float
    cost: float
    time: float

    @property
    def total_utility(self) -> float:
        return self.reward - self.risk - self.cost - self.time


class UtilityEngine:
    """
    Motor de Utilidade para avaliar e comparar alternativas de ação/rotas/inimigos.
    """

    def evaluate_encounter(self, enemy_name: str, enemy_level: int, world: WorldState) -> UtilityScore:
        """
        Avalia o combate contra um inimigo específico.
        """
        active = world.team.active_pokemon
        if not active:
            return UtilityScore(enemy_name, reward=10, risk=50, cost=10, time=20)

        # Cálculo heurístico simples de recompensa e risco
        reward = enemy_level * 15.0
        risk = (enemy_level / max(1, active.level)) * 20.0
        if active.hp_percentage < 0.3:
            risk += 40.0  # Risco elevado se HP do agente for baixo

        cost = 5.0
        estimated_time = 10.0

        return UtilityScore(
            action_name=f"Fight_{enemy_name}",
            reward=reward,
            risk=risk,
            cost=cost,
            time=estimated_time
        )

    def evaluate_goals(self, goals: list, world: WorldState) -> Dict[str, float]:
        """
        Pontua cada meta candidata usando a fórmula utility = reward - risk - cost - time.
        Retorna dicionário mapeando nome da meta para sua pontuação de utilidade final.
        """
        scores: Dict[str, float] = {}

        for g in goals:
            reward, risk, cost, time_penalty = 50.0, 10.0, 5.0, 5.0

            if g == "HEAL_TEAM":
                if world.team.needs_healing:
                    reward, risk = 120.0, 0.0
                else:
                    reward, risk = 0.0, 80.0
            elif g == "FOLLOW_PLAYER":
                reward = 80.0 if world.companion.is_following_leader else 70.0
                risk = 5.0
            elif g in ["FARM_XP", "HUNT"]:
                reward = 60.0
                if world.team.needs_healing:
                    risk = 90.0
            elif g == "EXPLORE":
                reward = 30.0

            utility = reward - risk - cost - time_penalty
            scores[g] = utility

        return scores
