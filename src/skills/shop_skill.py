"""
Shop Skill - Capacidade Modular de Compra de Suprimentos
=========================================================
"""

from typing import Any, Dict
from .base_skill import BaseSkill, SkillResult, SkillStatus
from ..world.world_state import WorldState


class ShopSkill(BaseSkill):
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(name="ShopSkill", config=config)

    def can_execute(self, world: WorldState) -> bool:
        return world.resources.money >= 200

    def execute(self, world: WorldState, components: Dict[str, Any]) -> SkillResult:
        world.resources.pokeballs_count += 5
        world.resources.money -= 1000
        return SkillResult(status=SkillStatus.SUCCESS, message="Compradas 5 Pokéballs na PokéMart!")

    def is_complete(self, world: WorldState) -> bool:
        return world.resources.pokeballs_count >= 5
