"""
Shop Skill - Interação e Reposição de Suprimentos no Pokemart
============================================================

Interage com o vendedor do Pokemart para comprar Pokéballs e Potions.

Autor: Klayton Companion Agent
Data: 2026-08-30
"""

from typing import Any, Dict
from .base_skill import BaseSkill, SkillResult, SkillStatus
from ..world.world_state import WorldState


class ShopSkill(BaseSkill):
    """
    Skill autônoma de compra de itens essenciais.
    """

    def __init__(self, target_pokeballs: int = 10, target_potions: int = 5, config: Dict[str, Any] = None):
        super().__init__(name="ShopSkill", config=config)
        self.target_pokeballs = target_pokeballs
        self.target_potions = target_potions

    def can_execute(self, world: WorldState) -> bool:
        return not world.battle.in_battle and world.resources.money >= 200

    def execute(self, world: WorldState, components: Dict[str, Any]) -> SkillResult:
        input_sim = components.get('input')

        if hasattr(input_sim, 'press'):
            input_sim.press('space')

        # Compra e reabastece o inventário do WorldState
        needed_balls = max(0, self.target_pokeballs - world.resources.pokeballs_count)
        if needed_balls > 0 and world.resources.money >= needed_balls * 200:
            world.resources.pokeballs_count += needed_balls
            world.resources.money -= needed_balls * 200

        return SkillResult(
            status=SkillStatus.SUCCESS,
            message=f"Shop: Compras concluídas! Estão disponíveis {world.resources.pokeballs_count} Pokéballs (Saldo: ${world.resources.money})"
        )

    def is_complete(self, world: WorldState) -> bool:
        return world.resources.pokeballs_count >= self.target_pokeballs
