"""
Execution Coordinator - Coordenador do Ciclo de Vida da Ação Ativa
===================================================================

Garante que uma ação do GOAP permaneça ativa enquanto a Skill retornar SkillStatus.RUNNING.
A ação só é consumida do plano (commit_current_action) quando a Skill terminar com SkillStatus.SUCCESS.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Dict, Any

from ..decision.goap_planner import GOAPAction, GOAPPlanner
from ..skills.base_skill import BaseSkill, SkillResult, SkillStatus
from ..world.world_state import WorldState
from ..decision.goal_engine import GoalInstance


@dataclass
class ActiveExecution:
    action: GOAPAction
    skill: BaseSkill
    goal: GoalInstance
    started: bool = False


class ExecutionCoordinator:
    """
    Coordenador de execução de ações do GOAP.
    Aplica o contrato estrito:
    - RUNNING: Mantém a ação ativa no plano.
    - SUCCESS: Confirma a ação no GOAPPlanner e avança para a próxima.
    - FAILED/BLOCKED/INTERRUPTED: Descarta a execução ativa e dispara replanejamento.
    """

    def __init__(self, planner: GOAPPlanner):
        self.planner = planner
        self.active: Optional[ActiveExecution] = None

    def reset(self) -> None:
        """Reseta a execução ativa."""
        self.active = None

    def interrupt(self, world: WorldState) -> None:
        """Cancela a Skill ativa e reseta o coordenador."""
        if self.active:
            try:
                self.active.skill.cancel(world)
            except Exception:
                pass
        self.active = None

    def _inject_goal_parameters(self, skill: BaseSkill, goal: GoalInstance) -> None:
        """Injeta parâmetros do objetivo na Skill de forma isolada."""
        if hasattr(skill, "target_level"):
            skill.target_level = goal.target_level
        if hasattr(skill, "target_pokemon"):
            skill.target_pokemon = goal.target
        if hasattr(skill, "target_map"):
            skill.target_map = goal.location_hint

    def _activate_next(
        self,
        goal: GoalInstance,
        world: WorldState,
    ) -> Optional[ActiveExecution]:

        planned = self.planner.peek_next_action(goal, world)
        if planned is None:
            return None

        action, skill = planned

        self.active = ActiveExecution(
            action=action,
            skill=skill,
            goal=goal,
        )

        return self.active

    def tick(
        self,
        goal: GoalInstance,
        world: WorldState,
        components: Dict[str, Any],
    ) -> SkillResult:

        if self.active is None:
            if self._activate_next(goal, world) is None:
                return SkillResult(
                    status=SkillStatus.SUCCESS,
                    message="Nenhuma ação necessária",
                )

        active = self.active

        # Se o Goal mudou mid-execution, cancela e solicita replanejamento
        if active.goal != goal and active.goal.type != goal.type:
            active.skill.cancel(world)
            self.active = None
            self.planner.trigger_replan()
            return SkillResult(
                status=SkillStatus.INTERRUPTED,
                message="Goal alterado; replanejamento solicitado",
            )

        # Ativação inicial da Skill
        if not active.started:
            if not active.skill.can_start(world):
                self.active = None
                self.planner.trigger_replan()
                return SkillResult(
                    status=SkillStatus.BLOCKED,
                    message=f"{active.skill.name} não pode iniciar",
                )

            # Limpa estado residual e injeta parâmetros do novo Goal
            active.skill.reset_runtime_state()
            self._inject_goal_parameters(active.skill, goal)

            active.skill.start({
                "goal": goal,
                "action": active.action,
            })
            active.started = True

        result = active.skill.update(world, components)

        if result.status == SkillStatus.RUNNING:
            return result

        if result.status == SkillStatus.SUCCESS:
            self.planner.commit_current_action(active.action)
            self.active = None
            return result

        if result.status in {
            SkillStatus.FAILED,
            SkillStatus.BLOCKED,
            SkillStatus.INTERRUPTED,
        }:
            self.active = None
            self.planner.trigger_replan()
            return result

        return result
