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
try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger("NavRecoveryEngine")


class NavRecoverySkillEngine:
    """
    Orquestrador Unificado da Tríade Mestra com Injeção Dinâmica de Parâmetros.
    """

    def __init__(self):
        self.navigation: NavigationSystem = NavigationSystem()
        self.recovery: RecoveryManager = RecoveryManager()
        self.goap_planner: GOAPPlanner = GOAPPlanner()
        self.hierarchical_planner: HierarchicalPlanner = HierarchicalPlanner()

    def execute_step(self, active_goal_input: Union[str, GoalInstance], world: WorldState, components: Dict[str, Any]) -> SkillResult:
        """
        Executa a Skill ativa e injeta target e target_level da GoalInstance na instância da Skill.
        """
        if isinstance(active_goal_input, GoalInstance):
            goal_instance = active_goal_input
            goal_name = goal_instance.name
        else:
            goal_name = str(active_goal_input)
            goal_instance = GoalInstance(type=Goal.from_string(goal_name))

        # 1. Obter a próxima Skill do GOAP / HierarchicalPlanner
        skill: Optional[BaseSkill] = self.goap_planner.get_next_skill(goal_instance, world)
        if not skill:
            skill = self.hierarchical_planner.resolve_next_skill(goal_name, world)

        if not skill:
            return SkillResult(status=SkillStatus.SUCCESS, message="Nenhuma Skill ativa necessária")

        # 2. Injeção dos parâmetros dinâmicos (target_level, target_pokemon, target_map) na Skill!
        if goal_instance.target_level and hasattr(skill, 'target_level'):
            setattr(skill, 'target_level', goal_instance.target_level)
            logger.info(f"🎯 Parâmetro Injetado na Skill {skill.name}: target_level={goal_instance.target_level}")

        if goal_instance.target and hasattr(skill, 'target_pokemon'):
            setattr(skill, 'target_pokemon', goal_instance.target)

        if goal_instance.location_hint and hasattr(skill, 'target_map'):
            setattr(skill, 'target_map', goal_instance.location_hint)
            logger.info(f"🗺️ Parâmetro Injetado na Skill {skill.name}: target_map='{goal_instance.location_hint}'")

        world.agent.active_skill = skill.name

        # 3. Execução da Skill
        result: SkillResult = skill.execute(world, components)

        # 4. Monitoramento de Colisão & Recuperação
        if world.player.position:
            moved_successfully = self.navigation.verify_local_step(world.player.position)
            if not moved_successfully or self.navigation.is_stuck:
                logger.warning(f"🚧 Estagnação detectada em {world.player.position}! Disparando RecoveryManager...")
                self.recovery.recover(world, components, reason="Position stuck in collision")
                self.navigation.reset_local()
                self.goap_planner.trigger_replan()
                return SkillResult(status=SkillStatus.INTERRUPTED, message="Interrompido para recuperação de obstáculo")

        if result.failed:
            logger.warning(f"🚨 Skill '{skill.name}' reportou falha! Disparando procedimento de recuperação...")
            self.recovery.recover(world, components, reason=f"Skill {skill.name} failed: {result.message}")
            self.goap_planner.trigger_replan()
            return SkillResult(status=SkillStatus.FAILED, message=f"Recuperado após falha da Skill {skill.name}")

        return result
