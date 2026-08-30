"""
Goal Manager - Conciliação de Objetivos Compartilhados e Pessoais
================================================================

Gerencia a coexistência entre o Objetivo Compartilhado (acordado com o humano, ex: TRAIN_TEAM)
e os Objetivos Pessoais do Klayton (motivação própria autônoma, ex: level_up(Pikachu)).

Autor: Klayton Companion Agent
Data: 2026-08-30
"""

from dataclasses import dataclass, field
from typing import Optional, List
from ..decision.goal_engine import Goal


@dataclass
class PersonalGoal:
    name: str
    target: str
    desired_value: Any
    current_value: Any = 0
    priority: float = 0.5


class CompanionGoalManager:
    """
    Gerenciador de Metas Compartilhadas vs Pessoais do Companheiro.
    """

    def __init__(self, primary_shared_goal: Goal = Goal.FOLLOW_PLAYER):
        self.shared_goal: Goal = primary_shared_goal
        self.personal_goals: List[PersonalGoal] = []
        self.active_personal_goal: Optional[PersonalGoal] = None

    def add_personal_goal(self, goal: PersonalGoal) -> None:
        self.personal_goals.append(goal)

    def select_active_goal(self, is_waiting: bool, team_needs_heal: bool) -> Goal:
        """
        Seleciona o objetivo ativo priorizando metas de segurança e compartilhadas,
        mas permitindo avanço em metas pessoais quando apropriado.
        """
        if team_needs_heal:
            return Goal.HEAL_TEAM

        if is_waiting:
            return Goal.IDLE

        # Se há um objetivo pessoal ativo e o compartilhado permite (ex: FOLLOW_PLAYER ou FARM_XP)
        if self.active_personal_goal and self.shared_goal in [Goal.FOLLOW_PLAYER, Goal.FARM_XP, Goal.HUNT]:
            return Goal.TRAIN_POKEMON

        return self.shared_goal
