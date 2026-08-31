"""
Quest Skill - Execução de Objetivos de História e Missões
=========================================================

Conecta-se ao QuestEngine para conduzir o agente até os objetivos de missões,
enfrentar líderes de ginásio e interagir com NPCs da história.

Autor: Klayton Companion Agent Framework
Data: 2026-08-30
"""

from typing import Any, Dict
from .base_skill import BaseSkill, SkillResult, SkillStatus
from ..world.world_state import WorldState
from ..world.quest_engine import QuestEngine, QuestStatus


class QuestSkill(BaseSkill):
    """
    Skill de progressão da história principal.
    """

    def __init__(self, quest_engine: QuestEngine = None, config: Dict[str, Any] = None):
        super().__init__(name="QuestSkill", config=config)
        self.quest_engine = quest_engine or QuestEngine()

    def can_execute(self, world: WorldState) -> bool:
        return not world.battle.in_battle

    def execute(self, world: WorldState, components: Dict[str, Any]) -> SkillResult:
        active_quest = self.quest_engine.get_active_quest()
        if not active_quest:
            return SkillResult(status=SkillStatus.SUCCESS, message="Todas as missões ativas concluídas!")

        obj = active_quest.current_objective
        if not obj:
            return SkillResult(status=SkillStatus.SUCCESS, message=f"Quest '{active_quest.title}' finalizada!")

        input_sim = components.get('input')
        if hasattr(input_sim, 'press'):
            input_sim.press('w')

        return SkillResult(
            status=SkillStatus.RUNNING,
            message=f"Progresso da Quest: [{active_quest.title}] ➔ {obj.description} (Destino: {obj.target_map})"
        )

    def is_complete(self, world: WorldState) -> bool:
        active = self.quest_engine.get_active_quest()
        return active is None or active.status == QuestStatus.COMPLETED
