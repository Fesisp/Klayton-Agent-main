"""
Fishing Skill - Capacidade Modular de Pesca
=============================================
"""

from typing import Any, Dict
from .base_skill import BaseSkill, SkillResult, SkillStatus
from ..world.world_state import WorldState


class FishingSkill(BaseSkill):
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(name="FishingSkill", config=config)

    def can_execute(self, world: WorldState) -> bool:
        return world.player.in_water or "water" in world.location.nearby_exits

    def execute(self, world: WorldState, components: Dict[str, Any]) -> SkillResult:
        input_sim = components.get('input')
        if hasattr(input_sim, 'press'):
            input_sim.press('1')  # Atalho de vara de pesca
        return SkillResult(status=SkillStatus.RUNNING, message="Lançando a vara de pesca na água...")

    def is_complete(self, world: WorldState) -> bool:
        return world.battle.in_battle
