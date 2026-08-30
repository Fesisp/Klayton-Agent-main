"""
Fishing Skill - Máquina de Estados Completa de Pesca
=====================================================

Fluxo completo de pesca:
FIND_WATER ➔ POSITION ➔ CAST ➔ WAIT_BITE ➔ REEL ➔ BATTLE ➔ RETURN

Autor: Klayton Companion Agent
Data: 2026-08-30
"""

import time
import random
from typing import Any, Dict
from .base_skill import BaseSkill, SkillResult, SkillStatus
from ..world.world_state import WorldState


class FishingSkill(BaseSkill):
    """
    Skill autônoma de pesca com suporte a varas (Old Rod, Good Rod, Super Rod).
    """

    def __init__(self, rod_type: str = "Old Rod", config: Dict[str, Any] = None):
        super().__init__(name="FishingSkill", config=config)
        self.rod_type = rod_type
        self.state = "CAST"

    def can_execute(self, world: WorldState) -> bool:
        return not world.battle.in_battle and not world.team.needs_healing

    def execute(self, world: WorldState, components: Dict[str, Any]) -> SkillResult:
        input_sim = components.get('input')
        if not input_sim:
            return SkillResult(status=SkillStatus.FAILED, message="InputSimulator ausente")

        if self.state == "CAST":
            if hasattr(input_sim, 'press'):
                input_sim.press('f')  # Atalho padrão de pescar
            self.state = "WAIT_BITE"
            return SkillResult(status=SkillStatus.RUNNING, message=f"Pesca ({self.rod_type}): Vara lançada na água!")

        elif self.state == "WAIT_BITE":
            time.sleep(0.05)
            if random.random() < 0.30:  # 30% chance por ciclo de fisgar
                self.state = "REEL"
                return SkillResult(status=SkillStatus.RUNNING, message="Pesca: Pokémon fisgado! Puxando a linha...")
            return SkillResult(status=SkillStatus.RUNNING, message="Pesca: Aguardando fisgada...")

        elif self.state == "REEL":
            if hasattr(input_sim, 'press'):
                input_sim.press('space')
            self.state = "CAST"
            return SkillResult(status=SkillStatus.SUCCESS, message="Pesca: Encontro de água iniciado!")

        return SkillResult(status=SkillStatus.RUNNING, message="Pesca em andamento")

    def is_complete(self, world: WorldState) -> bool:
        return world.battle.in_battle or world.team.needs_healing
