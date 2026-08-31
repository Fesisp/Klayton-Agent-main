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


from .autonomy.autonomy_controller import AutonomyController
from .autonomy.goal_candidate import GoalCandidate


class CompanionGoalManager:
    """
    Gerenciador de Metas que opera inteiramente sobre instâncias de objetivos (GoalInstance).
    """

    def __init__(self, primary_shared_goal: Goal = Goal.FOLLOW_PLAYER):
        self.shared_goal_instance: GoalInstance = GoalInstance(type=primary_shared_goal)
        self.personal_goals: List[PersonalGoal] = []
        self.active_personal_goal: Optional[PersonalGoal] = None
        self.utility_engine: UtilityEngine = UtilityEngine()
        self.autonomy_controller: AutonomyController = AutonomyController()

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
        self.active_personal_goal = goal

    def select_active_goal(self, is_waiting: bool, team_needs_heal: bool, world: Optional[WorldState] = None) -> GoalInstance:
        """
        Gera a lista de metas candidatas e usa a UtilityEngine para selecionar a melhor GoalInstance.
        Preserva target, target_level, location_hint e constraints no retorno.
        """
        if world is None:
            world = WorldState()
            world.companion.is_following_leader = not is_waiting

        # 1. Prioridade Absoluta: Ordens diretas do jogador (priority >= 2.0)
        if self.shared_goal_instance and self.shared_goal_instance.priority >= 2.0:
            return self.shared_goal_instance

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

        best_goal_type = Goal.from_string(best_goal_str)
        if best_goal_type == self.shared_goal_instance.type:
            return self.shared_goal_instance

        if best_goal_type in [Goal.TRAIN_POKEMON, Goal.FARM_XP, Goal.HUNT] and self.active_personal_goal:
            return GoalInstance(
                type=best_goal_type,
                target=self.active_personal_goal.target,
                target_level=int(self.active_personal_goal.desired_value) if isinstance(self.active_personal_goal.desired_value, int) else 35,
                location_hint=self.shared_goal_instance.location_hint,
                constraints=self.shared_goal_instance.constraints,
                success_conditions={"level": self.active_personal_goal.desired_value}
            )

        return GoalInstance(
            type=best_goal_type,
            target=self.shared_goal_instance.target,
            target_level=self.shared_goal_instance.target_level,
            location_hint=self.shared_goal_instance.location_hint,
            constraints=self.shared_goal_instance.constraints
        )
