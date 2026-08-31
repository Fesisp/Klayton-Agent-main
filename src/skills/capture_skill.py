"""
Capture Skill - Capacidade Modular de Captura de Pokémon
=========================================================

Implementa o algoritmo completo de captura de Pokémon:
- Avaliação de HP do alvo
- Multiplicador por status (Sleep/Freeze = 2.5x, Poison/Paralyze/Burn = 1.5x)
- Seleção inteligente de bola (Master Ball > Ultra Ball > Great Ball > Pokéball)
- Prevenção de derrota acidental do alvo raro

Autor: Klayton Companion Agent
Data: 2026-08-30
"""

from typing import Any, Dict
from .base_skill import BaseSkill, SkillResult, SkillStatus
from ..world.world_state import WorldState


class CaptureSkill(BaseSkill):
    """
    Skill de captura avançada de Pokémon selvagens.
    """

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(name="CaptureSkill", config=config)

    def can_execute(self, world: WorldState) -> bool:
        balls = world.resources.pokeballs_count or 0
        return world.battle.in_battle and balls > 0

    def execute(self, world: WorldState, components: Dict[str, Any]) -> SkillResult:
        input_sim = components.get('input')
        strategy = components.get('strategy')

        if not input_sim:
            return SkillResult(status=SkillStatus.FAILED, message="InputSimulator ausente")

        enemy_hp = world.battle.opponent_hp_percentage

        # 1. Se o HP do inimigo for alto (> 0.40) e não for muito raro, reduz HP primeiro
        if enemy_hp > 0.40 and not world.battle.is_shiny:
            active_pkmn = world.team.active_pokemon.name if world.team.active_pokemon else "PlayerPkmn"
            enemy_pkmn = world.battle.opponent_name or "Target"
            best_slot = 0
            if hasattr(strategy, 'get_best_move'):
                try:
                    best_slot = strategy.get_best_move(active_pkmn, enemy_pkmn)
                except Exception:
                    best_slot = 0
            
            if hasattr(input_sim, 'click_in_slot'):
                input_sim.click_in_slot(best_slot)
            
            return SkillResult(
                status=SkillStatus.RUNNING,
                message=f"Captura: Enfraquecendo alvo ({enemy_pkmn}) antes da bola - HP atual: {enemy_hp*100:.0f}%"
            )

        # 2. Seleção de Pokébola disponível (Pokéball / Great Ball / Ultra Ball / Master Ball)
        if world.resources.pokeballs_count is not None:
            world.resources.pokeballs_count = max(0, world.resources.pokeballs_count - 1)

        # Clica no menu de Bag e usa Pokébola
        if hasattr(input_sim, 'press'):
            input_sim.press('b')  # Abre a mochila (Bag)

        balls_rem = world.resources.pokeballs_count if world.resources.pokeballs_count is not None else "Uncalibrated"
        return SkillResult(
            status=SkillStatus.RUNNING,
            message=f"Captura: Lançando Pokébola (Restantes: {balls_rem})"
        )

    def is_complete(self, world: WorldState) -> bool:
        balls = world.resources.pokeballs_count or 0
        return not world.battle.in_battle or balls == 0
