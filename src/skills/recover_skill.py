"""
Recover Skill - Descolamento e Recuperação de Estagnação (Anti-Stuck)
====================================================================
"""

import random
import time
from typing import Any, Dict
from .base_skill import BaseSkill, SkillResult, SkillStatus
from ..world.world_state import WorldState


class RecoverSkill(BaseSkill):
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(name="RecoverSkill", config=config)

    def can_execute(self, world: WorldState) -> bool:
        return True

    def execute(self, world: WorldState, components: Dict[str, Any]) -> SkillResult:
        input_sim = components.get('input')
        if hasattr(input_sim, 'press'):
            # Passo 4-way de descolamento
            for dir_key in ['s', 'a', 'd', 'w']:
                input_sim.press(dir_key)
                time.sleep(0.05)

        return SkillResult(status=SkillStatus.SUCCESS, message="Recovery: Descolamento 4-way executado com sucesso!")

    def is_complete(self, world: WorldState) -> bool:
        return True
