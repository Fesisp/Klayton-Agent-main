"""
Battle Skill - Capacidade Modular de Combate
============================================

Encapsula o motor de batalha tático (BattleStrategy, PP tracking, inferência de dano).

Autor: Klayton Agent 2.0 Framework
Data: 2026-08-30
"""

from typing import Any, Dict
from .base_skill import BaseSkill, SkillResult, SkillStatus
from ..world.world_state import WorldState


class BattleSkill(BaseSkill):
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(name="BattleSkill", config=config)

    def can_execute(self, world: WorldState) -> bool:
        return world.battle.in_battle or world.battle.is_shiny

    def execute(self, world: WorldState, components: Dict[str, Any]) -> SkillResult:
        strategy = components.get('strategy')
        input_sim = components.get('input')
        
        if not strategy or not input_sim:
            return SkillResult(status=SkillStatus.FAILED, message="Componentes ausentes")

        # Exemplo de execução delegada à inteligência de batalha v2.5
        active_pkmn = world.team.active_pokemon.name if world.team.active_pokemon else "Unknown"
        enemy_pkmn = world.battle.opponent_name or "Wild Pokemon"
        
        best_slot = strategy.get_best_move(active_pkmn, enemy_pkmn)
        if best_slot != -1 and hasattr(input_sim, 'click_in_slot'):
            input_sim.click_in_slot(best_slot)
            return SkillResult(status=SkillStatus.RUNNING, message=f"Golpe executado slot {best_slot}")
        
        return SkillResult(status=SkillStatus.RUNNING, message="Aguardando turno de batalha")

    def is_complete(self, world: WorldState) -> bool:
        return not world.battle.in_battle
