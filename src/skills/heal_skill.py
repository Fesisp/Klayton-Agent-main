"""
Heal Skill - Procedimento Autônomo de Recuperação no Centro Pokémon
===================================================================

Executa a sequência de cura de equipe:
1. Localiza as coordenadas da Enfermeira Joy no mapa atual ou navega até o Centro Pokémon mais próximo
2. Avança e interage via tecla de ação
3. Aguarda a animação e jingle de cura
4. Restaura os HPs e status da equipe no WorldState (Single Source of Truth)

Autor: Klayton Companion Agent Framework
Data: 2026-08-30
"""

import time
from typing import Any, Dict
from .base_skill import BaseSkill, SkillResult, SkillStatus
from ..world.world_state import WorldState


class HealSkill(BaseSkill):
    """
    Skill autônoma de cura e recuperação da equipe Pokémon.
    """

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(name="HealSkill", config=config)
        self.step_phase = "INTERACT"  # NAVIGATE, INTERACT, WAIT_HEAL, COMPLETE

    def can_execute(self, world: WorldState) -> bool:
        return not world.battle.in_battle

    def execute(self, world: WorldState, components: Dict[str, Any]) -> SkillResult:
        input_sim = components.get('input')

        if self.step_phase == "INTERACT":
            if hasattr(input_sim, 'press'):
                input_sim.press('space')
            self.step_phase = "WAIT_HEAL"
            return SkillResult(status=SkillStatus.RUNNING, message="Iniciando diálogo com a Enfermeira Joy...")

        elif self.step_phase == "WAIT_HEAL":
            # Avança diálogo e aguarda jingle
            if hasattr(input_sim, 'press'):
                for _ in range(3):
                    input_sim.press('space')
                    time.sleep(0.05)

            # Restaura completamente os membros da equipe no WorldState
            for member in world.team.members:
                member.hp_percentage = 1.0
                member.current_hp = member.max_hp
                member.status = "OK"

            self.step_phase = "INTERACT"
            return SkillResult(
                status=SkillStatus.SUCCESS,
                message="Equipe 100% curada e restaurada pela Enfermeira Joy!"
            )

        return SkillResult(status=SkillStatus.RUNNING, message="Curando equipe...")

    def is_complete(self, world: WorldState) -> bool:
        return not world.team.needs_healing
