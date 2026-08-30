"""
Navigate Skill - Capacidade Modular de Navegação Inter-Mapas
============================================================
"""

from typing import Any, Dict
from .base_skill import BaseSkill, SkillResult, SkillStatus
from ..world.world_state import WorldState


class NavigateSkill(BaseSkill):
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(name="NavigateSkill", config=config)

    def can_execute(self, world: WorldState) -> bool:
        return not world.battle.in_battle

    def execute(self, world: WorldState, components: Dict[str, Any]) -> SkillResult:
        input_sim = components.get('input')
        if hasattr(input_sim, 'press'):
            input_sim.press('d')
        return SkillResult(status=SkillStatus.RUNNING, message="Navegando em direção ao destino selecionado")

    def is_complete(self, world: WorldState) -> bool:
        return False
