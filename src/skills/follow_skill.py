"""
Follow Skill - Capacidade Modular de Acompanhar o Líder
======================================================
"""

from typing import Any, Dict
from .base_skill import BaseSkill, SkillResult, SkillStatus
from ..world.world_state import WorldState


class FollowSkill(BaseSkill):
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(name="FollowSkill", config=config)

    def can_execute(self, world: WorldState) -> bool:
        return not world.battle.in_battle and not world.team.needs_healing

    def execute(self, world: WorldState, components: Dict[str, Any]) -> SkillResult:
        input_sim = components.get('input')
        if hasattr(input_sim, 'press'):
            input_sim.press('w')
        return SkillResult(status=SkillStatus.RUNNING, message="Acompanhando movimento do líder")

    def is_complete(self, world: WorldState) -> bool:
        return world.battle.in_battle or world.team.needs_healing
