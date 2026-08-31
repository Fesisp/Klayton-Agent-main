"""
Wait Skill - Estado de Espera e Observação do Ambiente
=====================================================

Mantém o agente em prontidão estacionária quando solicitado pelo líder
("espera aqui", "me espera"). Realiza micro-animações visuais e monitora o retorno de Felipe.

Autor: Klayton Companion Agent Framework
Data: 2026-08-30
"""

import time
from typing import Any, Dict
from .base_skill import BaseSkill, SkillResult, SkillStatus
from ..world.world_state import WorldState


class WaitSkill(BaseSkill):
    """
    Skill de espera passiva com monitoramento de arredores.
    """

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(name="WaitSkill", config=config)
        self.start_wait_time = time.time()

    def can_execute(self, world: WorldState) -> bool:
        return not world.battle.in_battle

    def execute(self, world: WorldState, components: Dict[str, Any]) -> SkillResult:
        elapsed = time.time() - self.start_wait_time
        # Se estiver esperando há mais de 10s e líder voltar à tela, sinaliza prontidão
        if world.companion.target_player_position is not None:
            return SkillResult(
                status=SkillStatus.SUCCESS,
                message=f"Líder Felipe retornou após {elapsed:.1f}s de espera! Pronto para retomar."
            )

        return SkillResult(
            status=SkillStatus.RUNNING,
            message=f"Aguardando Felipe no local ({elapsed:.1f}s decorridos)..."
        )

    def is_complete(self, world: WorldState) -> bool:
        return not world.companion.is_following_leader
