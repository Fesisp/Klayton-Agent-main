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
from typing import List, Dict, Any, Optional
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
        from ..skills.heal_skill import HealSkill
        from ..skills.follow_skill import FollowSkill
        from ..skills.capture_skill import CaptureSkill
        from ..skills.fishing_skill import FishingSkill
        from ..skills.farm_xp_skill import FarmXPSkill
        from ..skills.shop_skill import ShopSkill
        from ..skills.explore_skill import ExploreSkill
        from ..skills.return_to_player_skill import ReturnToPlayerSkill
        from ..skills.recover_skill import RecoverSkill

        self.skills: Dict[str, BaseSkill] = {
            "BattleSkill": BattleSkill(),
            "HuntingSkill": HuntingSkill(),
            "HealSkill": HealSkill(),
            "FollowSkill": FollowSkill(),
            "CaptureSkill": CaptureSkill(),
            "FishingSkill": FishingSkill(),
            "FarmXPSkill": FarmXPSkill(),
            "ShopSkill": ShopSkill(),
            "ExploreSkill": ExploreSkill(),
            "ReturnToPlayerSkill": ReturnToPlayerSkill(),
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
        elif goal_name in ["FARM_XP", "HUNT", "TRAIN_POKEMON"]:
            tasks.append(Task(name="ExploreAreaTask", target_skill_name="HuntingSkill"))
            tasks.append(Task(name="FightEncounterTask", target_skill_name="BattleSkill"))
        else:
            tasks.append(Task(name="FollowTask", target_skill_name="FollowSkill"))

        self.active_plan = Plan(goal_name=goal_name, tasks=tasks)
        return self.active_plan

    def resolve_next_skill(self, goal_name: str, world: WorldState, max_depth: int = 5) -> Optional[BaseSkill]:
        """
        Resolve a próxima Skill a ser executada a partir da Tarefa ativa no Plano.
        """
        if max_depth <= 0:
            return None

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
