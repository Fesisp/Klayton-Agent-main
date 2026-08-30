"""
Quest Skill - Capacidade Modular de Avanço de História
======================================================
"""

from typing import Any, Dict
from .base_skill import BaseSkill, SkillResult, SkillStatus
from ..world.world_state import WorldState


class QuestSkill(BaseSkill):
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(name="QuestSkill", config=config)

    def can_execute(self, world: WorldState) -> bool:
        return world.quest.active or world.quest.goto_button_visible or world.quest.talk_button_visible

    def execute(self, world: WorldState, components: Dict[str, Any]) -> SkillResult:
        input_sim = components.get('input')
        if world.quest.talk_button_visible and hasattr(input_sim, 'press'):
            input_sim.press('space')
            return SkillResult(status=SkillStatus.RUNNING, message="Interagindo com NPC de quest...")
        elif world.quest.goto_button_visible and hasattr(input_sim, 'press'):
            input_sim.press('w')
            return SkillResult(status=SkillStatus.RUNNING, message="Deslocando até o objetivo da quest...")

        return SkillResult(status=SkillStatus.RUNNING, message="Acompanhando progresso da quest ativa")

    def is_complete(self, world: WorldState) -> bool:
        return not world.quest.active
