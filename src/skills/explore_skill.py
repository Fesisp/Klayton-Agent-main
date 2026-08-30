"""
Explore Skill - Exploração de Áreas Não Visitadas
===================================================
"""

import random
from typing import Any, Dict
from .base_skill import BaseSkill, SkillResult, SkillStatus
from ..world.world_state import WorldState


class ExploreSkill(BaseSkill):
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(name="ExploreSkill", config=config)

    def can_execute(self, world: WorldState) -> bool:
        return not world.battle.in_battle

    def execute(self, world: WorldState, components: Dict[str, Any]) -> SkillResult:
        input_sim = components.get('input')
        direction = random.choice(['w', 'a', 's', 'd'])
        if hasattr(input_sim, 'press'):
            input_sim.press(direction)
        return SkillResult(status=SkillStatus.RUNNING, message=f"Explorando mapa na direção '{direction}'")

    def is_complete(self, world: WorldState) -> bool:
        return world.battle.in_battle
