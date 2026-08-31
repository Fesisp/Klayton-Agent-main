"""
Interaction Skill - Interação com NPCs, Placas, Baús e Objetos do Mundo
========================================================================

Executa interações com elementos do cenário, avança diálogos e coleta itens.

Autor: Klayton Companion Agent Framework
Data: 2026-08-30
"""

import time
from typing import Any, Dict, Optional
from .base_skill import BaseSkill, SkillResult, SkillStatus
from ..world.world_state import WorldState


class InteractionSkill(BaseSkill):
    """
    Skill de interação contextual com NPCs e objetos.
    """

    def __init__(self, target_npc: Optional[str] = None, config: Dict[str, Any] = None):
        super().__init__(name="InteractionSkill", config=config)
        self.target_npc = target_npc

    def can_execute(self, world: WorldState) -> bool:
        return not world.battle.in_battle

    def execute(self, world: WorldState, components: Dict[str, Any]) -> SkillResult:
        input_sim = components.get('input')

        if hasattr(input_sim, 'press'):
            input_sim.press('space')

        target_desc = self.target_npc or "NPC/Objeto à frente"
        return SkillResult(
            status=SkillStatus.SUCCESS,
            message=f"Interagindo com {target_desc} e avançando diálogos"
        )

    def is_complete(self, world: WorldState) -> bool:
        return True
