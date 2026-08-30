"""
Wait Skill - Capacidade Modular de Aguardar no Local
====================================================
"""

from typing import Any, Dict
from .base_skill import BaseSkill, SkillResult, SkillStatus
from ..world.world_state import WorldState


class WaitSkill(BaseSkill):
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(name="WaitSkill", config=config)

    def can_execute(self, world: WorldState) -> bool:
        return True

    def execute(self, world: WorldState, components: Dict[str, Any]) -> SkillResult:
        return SkillResult(status=SkillStatus.RUNNING, message="Aguardando no local conforme instrução")

    def is_complete(self, world: WorldState) -> bool:
        return False
