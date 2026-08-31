"""
NavRecoverySkillEngine - Orquestrador da Tríade Mestra Unificada
================================================================

Unifica a arquitetura em 5 camadas:
GoalInstance ➔ Utility AI ➔ GOAPPlanner (A* Strategic Plan) ➔ HierarchicalPlanner ➔ Skill Queue

Contém resiliência com NavigationSystem (monitoramento de posição) e RecoveryManager (escape 4-way).

Autor: Klayton Companion Agent Framework
Data: 2026-08-30
"""

from typing import Dict, Any, Optional
from ..world.world_state import WorldState
from ..skills.base_skill import BaseSkill, SkillResult, SkillStatus
from ..navigation.navigation_system import NavigationSystem
from ..core.recovery_manager import RecoveryManager
from ..decision.goap_planner import GOAPPlanner
from ..decision.hierarchical_planner import HierarchicalPlanner
try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger("NavRecoveryEngine")


class NavRecoverySkillEngine:
    """
    Orquestrador Unificado da Tríade Mestra (GOAP + Hierarchical + Nav + Recovery).
    """

    def __init__(self):
        self.navigation: NavigationSystem = NavigationSystem()
        self.recovery: RecoveryManager = RecoveryManager()
        self.goap_planner: GOAPPlanner = GOAPPlanner()
        self.hierarchical_planner: HierarchicalPlanner = HierarchicalPlanner()

    def execute_step(self, current_goal: str, world: WorldState, components: Dict[str, Any]) -> SkillResult:
        """
        Executa o ciclo unificado:
        1. GOAPPlanner resolve a próxima Skill estratégica com busca A* e suporte a interrupção/retomada.
        2. Se necessário, o HierarchicalPlanner decompõe tarefas complexas.
        3. A Skill é executada e protegida por monitoramento de estagnação do NavigationSystem e RecoveryManager.
        """
        # 1. Obter a próxima Skill estratégica do GOAP
        skill: Optional[BaseSkill] = self.goap_planner.get_next_skill(current_goal, world)

        # Fallback de decomposição hierárquica se o GOAP não retornar skill imediata
        if not skill:
            skill = self.hierarchical_planner.resolve_next_skill(current_goal, world)

        if not skill:
            return SkillResult(status=SkillStatus.SUCCESS, message="Nenhuma Skill ativa necessária")

        world.agent.active_skill = skill.name

        # 2. Executar o ciclo da Skill
        result: SkillResult = skill.execute(world, components)

        # 3. Monitoramento de Navegação e Posição (Se houver posição registrada)
        if world.player.position:
            moved_successfully = self.navigation.verify_local_step(world.player.position)
            if not moved_successfully or self.navigation.is_stuck:
                logger.warning(f"🚧 Estagnação de posição detectada em {world.player.position}! Disparando RecoveryManager...")
                self.recovery.recover(world, components, reason="Position stuck in collision")
                self.navigation.reset_local()
                self.goap_planner.trigger_replan()
                return SkillResult(status=SkillStatus.INTERRUPTED, message="Interrompido para recuperação de obstáculo")

        # 4. Tratamento de Falha da própria Skill
        if result.failed:
            logger.warning(f"🚨 Skill '{skill.name}' reportou falha! Disparando procedimento de recuperação...")
            self.recovery.recover(world, components, reason=f"Skill {skill.name} failed: {result.message}")
            self.goap_planner.trigger_replan()
            return SkillResult(status=SkillStatus.FAILED, message=f"Recuperado após falha da Skill {skill.name}")

        return result
