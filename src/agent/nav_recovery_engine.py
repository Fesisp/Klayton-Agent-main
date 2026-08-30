"""
NavRecoverySkillEngine - Orquestrador da Tríade Mestra (Navigation + Recovery + Skills)
======================================================================================

Unifica o Roteamento de Navegação (Local/Global), o Verificador de Movimento e o Gerenciador de Recuperação
com a Fila de Skills em uma máquina de execução resiliente e impossível de travar.

Fluxo:
1. Avalia rota de navegação se necessário.
2. Executa o ciclo da Skill ativa.
3. Monitora se a posição mudou ou colidiu em obstáculo.
4. Se houver falha/estagnação ➔ Ativa o RecoveryManager (escape 4-way) e dispara REPLAN.

Autor: Klayton Companion Agent Framework
Data: 2026-08-30
"""

from typing import Dict, Any, Optional
from ..world.world_state import WorldState
from ..skills.base_skill import BaseSkill, SkillResult, SkillStatus
from ..navigation.navigation_system import NavigationSystem
from ..core.recovery_manager import RecoveryManager
from ..decision.hierarchical_planner import HierarchicalPlanner
try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger("NavRecoveryEngine")


class NavRecoverySkillEngine:
    """
    Orquestrador Unificado da Tríade Mestra.
    """

    def __init__(self):
        self.navigation: NavigationSystem = NavigationSystem()
        self.recovery: RecoveryManager = RecoveryManager()
        self.planner: HierarchicalPlanner = HierarchicalPlanner()

    def execute_step(self, current_goal: str, world: WorldState, components: Dict[str, Any]) -> SkillResult:
        """
        Executa um ciclo completo de execução da Skill ativa com proteção de navegação e recovery.
        """
        # 1. Obter a próxima Skill a ser executada a partir do HierarchicalPlanner
        skill: Optional[BaseSkill] = self.planner.resolve_next_skill(current_goal, world)
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
                self.planner.create_plan_for_goal(current_goal, world)
                return SkillResult(status=SkillStatus.INTERRUPTED, message="Interrompido para recuperação de obstáculo")

        # 4. Tratamento de Falha da própria Skill
        if result.failed:
            logger.warning(f"🚨 Skill '{skill.name}' reportou falha! Disparando procedimento de recuperação...")
            self.recovery.recover(world, components, reason=f"Skill {skill.name} failed: {result.message}")
            self.planner.create_plan_for_goal(current_goal, world)
            return SkillResult(status=SkillStatus.FAILED, message=f"Recuperado após falha da Skill {skill.name}")

        return result
