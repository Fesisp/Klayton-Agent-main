"""
NavRecoverySkillEngine - Orquestrador da Tríade Mestra (Injeção de Parâmetros de GoalInstance)
=============================================================================================

Garante que os parâmetros target e target_level da GoalInstance sejam injetados
diretamente na Skill ativa executada pelo Klayton.

Autor: Klayton Companion Agent Framework
Data: 2026-08-30
"""

from typing import Dict, Any, Optional, Union
from ..world.world_state import WorldState
from ..skills.base_skill import BaseSkill, SkillResult, SkillStatus
from ..navigation.navigation_system import NavigationSystem
from ..core.recovery_manager import RecoveryManager
from ..decision.goap_planner import GOAPPlanner
from ..decision.hierarchical_planner import HierarchicalPlanner
from ..decision.goal_engine import GoalInstance, Goal
from .execution_coordinator import ExecutionCoordinator

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger("NavRecoveryEngine")


class NavRecoverySkillEngine:
    """
    Orquestrador Unificado da Tríade Mestra com Injeção Dinâmica de Parâmetros e Coordenador de Execução.
    """

    def __init__(self):
        self.navigation: NavigationSystem = NavigationSystem()
        self.recovery: RecoveryManager = RecoveryManager()
        self.goap_planner: GOAPPlanner = GOAPPlanner()
        self.hierarchical_planner: HierarchicalPlanner = HierarchicalPlanner()
        self.execution: ExecutionCoordinator = ExecutionCoordinator(self.goap_planner)

    def execute_step(self, active_goal_input: Union[str, GoalInstance], world: WorldState, components: Dict[str, Any]) -> SkillResult:
        """
        Executa o tick da Skill ativa via ExecutionCoordinator, mantendo ações RUNNING ativas.
        """
        if isinstance(active_goal_input, GoalInstance):
            goal_instance = active_goal_input
        else:
            goal_name = str(active_goal_input)
            goal_instance = GoalInstance(type=Goal.from_string(goal_name))

        # Execução pelo ExecutionCoordinator (Garante que RUNNING não remove a ação do plano)
        result: SkillResult = self.execution.tick(goal_instance, world, components)

        if self.execution.active and self.execution.active.skill:
            world.agent.active_skill = self.execution.active.skill.name

        # 4. Monitoramento de Colisão & Recuperação
        if world.player.position and result.status == SkillStatus.RUNNING:
            moved_successfully = self.navigation.verify_local_step(world.player.position)
            if not moved_successfully or self.navigation.is_stuck:
                logger.warning(f"🚧 Estagnação detectada em {world.player.position}! Disparando RecoveryManager...")
                self.recovery.recover(world, components, reason="Position stuck in collision")
                self.navigation.reset_local()
                self.execution.interrupt(world)
                self.goap_planner.trigger_replan()
                return SkillResult(status=SkillStatus.INTERRUPTED, message="Interrompido para recuperação de obstáculo")

        if result.failed:
            logger.warning(f"🚨 Skill reportou falha! Disparando procedimento de recuperação...")
            self.recovery.recover(world, components, reason=f"Skill failed: {result.message}")
            self.execution.interrupt(world)
            self.goap_planner.trigger_replan()
            return SkillResult(status=SkillStatus.FAILED, message=f"Recuperado após falha da Skill: {result.message}")

        return result
