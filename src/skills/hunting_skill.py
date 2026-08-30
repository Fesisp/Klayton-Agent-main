"""
Hunting Skill - Capacidade Modular de Caça e Movimento
======================================================

Encapsula o padrão de caminhada humanizada em áreas delimitadas ou busca direcional.

Autor: Klayton Agent 2.0 Framework
Data: 2026-08-30
"""

import random
import time
from typing import Any, Dict
from .base_skill import BaseSkill, SkillResult
from ..world.world_state import WorldState


class HuntingSkill(BaseSkill):
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(name="HuntingSkill", config=config)

    def can_execute(self, world: WorldState) -> bool:
        return not world.battle.in_battle and not world.team.needs_healing

    def execute(self, world: WorldState, components: Dict[str, Any]) -> SkillResult:
        input_sim = components.get('input')
        if not input_sim:
            return SkillResult(success=False, failed=True, message="InputSimulator ausente")

        # Escolhe direção aleatória humanizada
        directions = ['w', 'a', 's', 'd']
        direction = random.choice(directions)
        input_sim.press(direction)
        time.sleep(0.1)

        return SkillResult(success=True, completed=False, message=f"Passo dado na direção {direction}")

    def is_complete(self, world: WorldState) -> bool:
        return world.battle.in_battle or world.team.needs_healing
