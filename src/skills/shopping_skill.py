"""
Shopping Skill - Gerenciamento de Recursos e Compras no Pokemart
================================================================

Compra itens consumíveis essenciais (Pokéballs, Potions, Antidotes)
respeitando a reserva de dinheiro de segurança.

Autor: Klayton Companion Agent Framework
Data: 2026-08-30
"""

from typing import Any, Dict
from .base_skill import BaseSkill, SkillResult, SkillStatus
from ..world.world_state import WorldState


class ShoppingSkill(BaseSkill):
    """
    Skill de compras automáticas de suprimentos.
    """

    def __init__(self, target_pokeballs: int = 15, target_potions: int = 5, config: Dict[str, Any] = None):
        super().__init__(name="ShoppingSkill", config=config)
        self.target_pokeballs = target_pokeballs
        self.target_potions = target_potions

    def can_execute(self, world: WorldState) -> bool:
        money = world.resources.money or 0
        return not world.battle.in_battle and money >= 200

    def execute(self, world: WorldState, components: Dict[str, Any]) -> SkillResult:
        input_sim = components.get('input')

        if hasattr(input_sim, 'press'):
            input_sim.press('space')

        cur_balls = world.resources.pokeballs_count or 0
        cur_money = world.resources.money or 0
        needed_balls = max(0, self.target_pokeballs - cur_balls)
        cost_balls = needed_balls * 200

        if needed_balls > 0 and cur_money >= cost_balls:
            world.resources.pokeballs_count = cur_balls + needed_balls
            world.resources.money = cur_money - cost_balls

        return SkillResult(
            status=SkillStatus.SUCCESS,
            message=f"Shopping: Estoque renovado! Pokéballs: {world.resources.pokeballs_count} (Saldo restante: ${world.resources.money})"
        )

    def is_complete(self, world: WorldState) -> bool:
        cur_balls = world.resources.pokeballs_count or 0
        return cur_balls >= self.target_pokeballs
