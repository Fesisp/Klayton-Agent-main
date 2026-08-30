"""
Return To Player Skill - Retorno Rápido ao Líder Felipe
======================================================
"""

from typing import Any, Dict
from .base_skill import BaseSkill, SkillResult, SkillStatus
from ..world.world_state import WorldState


class ReturnToPlayerSkill(BaseSkill):
    def __init__(self, target_player: str = "Felipe", config: Dict[str, Any] = None):
        super().__init__(name="ReturnToPlayerSkill", config=config)
        self.target_player = target_player

    def can_execute(self, world: WorldState) -> bool:
        return not world.battle.in_battle

    def execute(self, world: WorldState, components: Dict[str, Any]) -> SkillResult:
        input_sim = components.get('input')
        if hasattr(input_sim, 'press'):
            input_sim.press('w')
        world.companion.is_following_leader = True
        return SkillResult(status=SkillStatus.SUCCESS, message=f"Retornado ao alinhamento com {self.target_player}")

    def is_complete(self, world: WorldState) -> bool:
        return world.companion.is_following_leader
