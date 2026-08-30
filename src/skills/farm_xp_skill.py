"""
Farm XP Skill - Skill de Treinamento e Ganho de Experiência
=============================================================

Gerencia o ciclo completo de treinamento:
- Medição de métricas (encounters, XP/hour)
- Retorno automático ao Centro Pokémon quando HP < 20% ou PP esgotar

Autor: Klayton Companion Agent
Data: 2026-08-30
"""

import time
from typing import Any, Dict
from .base_skill import BaseSkill, SkillResult, SkillStatus
from ..world.world_state import WorldState


class FarmXPSkill(BaseSkill):
    """
    Skill de ganho autônomo de experiência e treinamento de equipe.
    """

    def __init__(self, target_level: int = 35, config: Dict[str, Any] = None):
        super().__init__(name="FarmXPSkill", config=config)
        self.target_level = target_level
        self.encounters_count = 0
        self.start_time = time.time()

    def can_execute(self, world: WorldState) -> bool:
        return not world.team.needs_healing

    def execute(self, world: WorldState, components: Dict[str, Any]) -> SkillResult:
        input_sim = components.get('input')

        if world.team.needs_healing:
            return SkillResult(status=SkillStatus.INTERRUPTED, message="FarmXP: Equipe necessita de cura. Retornando ao Center.")

        active_pkmn = world.team.active_pokemon
        current_lvl = active_pkmn.level if active_pkmn else 1

        if current_lvl >= self.target_level:
            return SkillResult(status=SkillStatus.SUCCESS, message=f"FarmXP: Meta atingida! Pokémon nível {current_lvl} >= {self.target_level}")

        if world.battle.in_battle:
            return SkillResult(status=SkillStatus.RUNNING, message=f"FarmXP: Em combate de treinamento (Nível atual: {current_lvl}/{self.target_level})")

        # Se estiver explorando, realiza passos de caminhada na grama
        if hasattr(input_sim, 'press'):
            input_sim.press('w')

        self.encounters_count += 1
        elapsed_hours = max(0.001, (time.time() - self.start_time) / 3600.0)
        rate = self.encounters_count / elapsed_hours

        return SkillResult(
            status=SkillStatus.RUNNING,
            message=f"FarmXP: Procurando encontros na grama (Nível: {current_lvl}/{self.target_level} | Taxa: {rate:.0f} encounters/h)"
        )

    def is_complete(self, world: WorldState) -> bool:
        active = world.team.active_pokemon
        return (active is not None and active.level >= self.target_level) or world.team.needs_healing
