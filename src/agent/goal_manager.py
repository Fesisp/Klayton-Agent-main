"""
Goal Manager - Conciliação de Objetivos Parametrizados via Utility AI
======================================================================

Gerencia a seleção e conciliação de GoalInstances (parametrizados com target e constraints)
e utiliza a UtilityEngine como tomadora de decisão soberana.

Autor: Klayton Companion Agent
Data: 2026-08-30
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from ..decision.goal_engine import Goal, GoalInstance
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
    Gerenciador de Metas que opera inteiramente sobre instâncias de objetivos (GoalInstance).
    """

    def __init__(self, primary_shared_goal: Goal = Goal.FOLLOW_PLAYER):
        self.shared_goal_instance: GoalInstance = GoalInstance(type=primary_shared_goal)
        self.personal_goals: List[PersonalGoal] = []
        self.active_personal_goal: Optional[PersonalGoal] = None
        self.utility_engine: UtilityEngine = UtilityEngine()

    @property
    def shared_goal(self) -> Goal:
        return self.shared_goal_instance.type

    @shared_goal.setter
    def shared_goal(self, val: Goal) -> None:
        self.shared_goal_instance = GoalInstance(type=val)

    def set_shared_goal_instance(self, instance: GoalInstance) -> None:
        """Define a instância completa do objetivo compartilhado preservando alvos e restrições."""
        self.shared_goal_instance = instance

    def add_personal_goal(self, goal: PersonalGoal) -> None:
        """Adiciona e ativa imediatamente a meta pessoal para avaliação na Utility AI."""
        self.personal_goals.append(goal)
        self.active_personal_goal = goal  # BUG 3 CORRIGIDO: Ativação explícita da meta pessoal

    def select_active_goal(self, is_waiting: bool, team_needs_heal: bool, world: Optional[WorldState] = None) -> GoalInstance:
        """
        Gera a lista de metas candidatas e usa a UtilityEngine para selecionar a melhor GoalInstance.
        Preserva target e target_level no retorno.
        """
        if world is None:
            world = WorldState()
            world.companion.is_following_leader = not is_waiting

        candidate_goals: List[str] = [
            "HEAL_TEAM",
            "FOLLOW_PLAYER",
            self.shared_goal_instance.name
        ]

        if is_waiting:
            candidate_goals.append("IDLE")

        if self.active_personal_goal:
            candidate_goals.append("TRAIN_POKEMON")

        candidate_goals = list(dict.fromkeys(candidate_goals))
        best_goal_str, scores = self.utility_engine.select_best_goal(candidate_goals, world)

        # Se o objetivo vencedor for o compartilhado ou o de treino pessoal, repassa os parâmetros!
        best_goal_type = Goal.from_string(best_goal_str)
        if best_goal_type == self.shared_goal_instance.type:
            return self.shared_goal_instance

        if best_goal_type == Goal.TRAIN_POKEMON and self.active_personal_goal:
            return GoalInstance(
                type=Goal.TRAIN_POKEMON,
                target=self.active_personal_goal.target,
                target_level=int(self.active_personal_goal.desired_value) if isinstance(self.active_personal_goal.desired_value, int) else 35,
                success_conditions={"level": self.active_personal_goal.desired_value}
            )

        return GoalInstance(type=best_goal_type)
