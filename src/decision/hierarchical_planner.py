"""
Hierarchical Planner - Planejamento Hierárquico (Goal -> Plan -> Task -> Skill)
================================================================================

Diferencia o GoalManager (gerenciamento de intenções) do Planejador Hierárquico.
Decompõe um Goal em um Plano composto por Tarefas (Tasks), que são mapeadas para Skills.

Fluxo:
Goal -> Plan -> Tasks -> Skills

Autor: Klayton Companion Agent
Data: 2026-08-30
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Union
from .goal_engine import GoalInstance, Goal
from ..world.world_state import WorldState
from ..skills.base_skill import BaseSkill
from ..skills.battle_skill import BattleSkill
from ..skills.hunting_skill import HuntingSkill
try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger("HierarchicalPlanner")


@dataclass
class Task:
    """Uma tarefa individual dentro de um plano."""
    name: str
    target_skill_name: str
    preconditions: Dict[str, Any] = field(default_factory=dict)
    completed: bool = False


@dataclass
class Plan:
    """Um plano composto por uma sequência de tarefas."""
    goal_name: str
    tasks: List[Task] = field(default_factory=list)
    current_task_index: int = 0

    @property
    def current_task(self) -> Optional[Task]:
        if 0 <= self.current_task_index < len(self.tasks):
            return self.tasks[self.current_task_index]
        return None

    @property
    def is_finished(self) -> bool:
        return self.current_task_index >= len(self.tasks)


class HierarchicalPlanner:
    """
    Planejador Hierárquico que desdobra Metas em Planos e Tarefas.
    """

    def __init__(self):
        from ..skills import (
            FollowSkill, WaitSkill, NavigateSkill, HealSkill,
            BattleSkill, HuntingSkill, CaptureSkill, FishingSkill,
            InteractionSkill, ShoppingSkill, QuestSkill, ExploreSkill,
            RecoverSkill
        )

        self.skills: Dict[str, BaseSkill] = {
            "FollowSkill": FollowSkill(),
            "WaitSkill": WaitSkill(),
            "NavigateSkill": NavigateSkill(),
            "HealSkill": HealSkill(),
            "BattleSkill": BattleSkill(),
            "HuntingSkill": HuntingSkill(),
            "CaptureSkill": CaptureSkill(),
            "FishingSkill": FishingSkill(),
            "InteractionSkill": InteractionSkill(),
            "ShoppingSkill": ShoppingSkill(),
            "QuestSkill": QuestSkill(),
            "ExploreSkill": ExploreSkill(),
            "RecoverSkill": RecoverSkill(),
        }
        self.active_plan: Optional[Plan] = None

    def create_plan_for_goal(self, goal_name: str, world: WorldState) -> Plan:
        """
        Decompõe o Goal em um Plano de Tarefas.
        """
        logger.info(f"🧩 Construindo Plano Hierárquico para o Goal: {goal_name}")
        tasks: List[Task] = []

        if world.team.needs_healing:
            tasks.append(Task(name="HealTeamTask", target_skill_name="HealSkill"))
        elif world.battle.in_battle:
            tasks.append(Task(name="FightBattleTask", target_skill_name="BattleSkill"))
        elif goal_name in ["FARM_XP", "TRAIN_POKEMON"]:
            # Meta Composta FARM_XP: Navigate -> Hunt -> Battle -> (Heal if needed) -> Resume
            tasks.append(Task(name="NavigateToSpot", target_skill_name="NavigateSkill"))
            tasks.append(Task(name="HuntEncounter", target_skill_name="HuntingSkill"))
            tasks.append(Task(name="FightBattle", target_skill_name="BattleSkill"))
        elif goal_name in ["SHOP", "BUY_ITEMS"]:
            tasks.append(Task(name="NavigateToMart", target_skill_name="NavigateSkill"))
            tasks.append(Task(name="BuySupplies", target_skill_name="ShoppingSkill"))
        elif goal_name in ["PROGRESS_STORY", "QUEST"]:
            tasks.append(Task(name="ExecuteQuest", target_skill_name="QuestSkill"))
        elif goal_name in ["WAIT", "IDLE"]:
            tasks.append(Task(name="WaitTask", target_skill_name="WaitSkill"))
        else:
            tasks.append(Task(name="FollowTask", target_skill_name="FollowSkill"))

        self.active_plan = Plan(goal_name=goal_name, tasks=tasks)
        return self.active_plan

    def resolve_next_skill(self, goal_input: Union[str, GoalInstance], world: WorldState, max_depth: int = 5) -> Optional[BaseSkill]:
        """
        Resolve a próxima Skill a ser executada a partir da Tarefa ativa no Plano.
        """
        if max_depth <= 0:
            return None

        if isinstance(goal_input, GoalInstance):
            goal_name = goal_input.name
        else:
            goal_name = str(goal_input)

        if not self.active_plan or self.active_plan.goal_name != goal_name or self.active_plan.is_finished:
            self.create_plan_for_goal(goal_name, world)

        if self.active_plan and not self.active_plan.is_finished:
            task = self.active_plan.current_task
            if task and task.target_skill_name in self.skills:
                skill = self.skills[task.target_skill_name]
                if skill.is_complete(world):
                    task.completed = True
                    self.active_plan.current_task_index += 1
                    return self.resolve_next_skill(goal_name, world, max_depth=max_depth - 1)
                return skill

        return None
