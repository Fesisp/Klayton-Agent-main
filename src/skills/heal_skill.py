"""
Heal Skill - Capacidade Modular de Cura no Pokémon Center
==========================================================
"""

from typing import Any, Dict
from .base_skill import BaseSkill, SkillResult, SkillStatus
from ..world.world_state import WorldState


class HealSkill(BaseSkill):
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(name="HealSkill", config=config)

    def can_execute(self, world: WorldState) -> bool:
        return world.team.needs_healing

    def execute(self, world: WorldState, components: Dict[str, Any]) -> SkillResult:
        input_sim = components.get('input')
        if hasattr(input_sim, 'press'):
            input_sim.press('space')
        
        # Simula restauração de HP da equipe
        for pkmn in world.team.members:
            pkmn.hp_percentage = 1.0
            pkmn.status = "OK"

        return SkillResult(status=SkillStatus.SUCCESS, message="Equipe totalmente curada no Pokémon Center!")

    def is_complete(self, world: WorldState) -> bool:
        return not world.team.needs_healing
