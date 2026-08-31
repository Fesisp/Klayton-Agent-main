"""
Goal Manager - Conciliação de Objetivos via Utility AI
======================================================

Gera metas candidatas (compartilhadas e pessoais) e utiliza a UtilityEngine
como TOMADORA DE DECISÃO SOBERANA no loop principal do Klayton.

Equação de decisão:
utility = reward - risk - cost - time

Autor: Klayton Companion Agent
Data: 2026-08-30
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from ..decision.goal_engine import Goal
from ..decision.utility_engine import UtilityEngine
from ..world.world_state import WorldState


@dataclass
class PersonalGoal:
    name: str
    target: str
    desired_value: Any
    current_value: Any = 0
    priority: float = 0.5


class CompanionGoalManager:
    """
    Gerenciador de Metas que delega a decisão de seleção para a UtilityEngine.
    """

    def __init__(self, primary_shared_goal: Goal = Goal.FOLLOW_PLAYER):
        self.shared_goal: Goal = primary_shared_goal
        self.personal_goals: List[PersonalGoal] = []
        self.active_personal_goal: Optional[PersonalGoal] = None
        self.utility_engine: UtilityEngine = UtilityEngine()

    def add_personal_goal(self, goal: PersonalGoal) -> None:
        self.personal_goals.append(goal)

    def select_active_goal(self, is_waiting: bool, team_needs_heal: bool, world: Optional[WorldState] = None) -> Goal:
        """
        Gera a lista de metas candidatas viáveis e utiliza a UtilityEngine
        para calcular a utilidade de cada uma em tempo real, selecionando o objetivo vencedor.
        """
        # Se não houver WorldState explícito, constrói um temporário para reflexão
        if world is None:
            world = WorldState()
            world.team.needs_healing = team_needs_heal
            world.companion.is_following_leader = not is_waiting

        # 1. Monta o catálogo de metas candidatas no estado atual
        candidate_goals: List[str] = [
            "HEAL_TEAM",
            "FOLLOW_PLAYER",
            self.shared_goal.name
        ]

        if is_waiting:
            candidate_goals.append("IDLE")

        if self.active_personal_goal:
            candidate_goals.append("TRAIN_POKEMON")

        candidate_goals.append("EXPLORE")

        # Elimina duplicatas preservando a ordem
        candidate_goals = list(dict.fromkeys(candidate_goals))

        # 2. A UtilityEngine escolhe racionalmente com base em (reward - risk - cost - time)
        best_goal_str, scores = self.utility_engine.select_best_goal(candidate_goals, world)

        # 3. Retorna o Enum Goal correspondente à maior utilidade
        return Goal.from_string(best_goal_str)
