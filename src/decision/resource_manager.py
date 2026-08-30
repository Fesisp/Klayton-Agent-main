"""
Resource Manager - Gestão de Recursos e Sobrevivência (Fase 7 do Roadmap)
========================================================================

Monitora níveis de HP, PP, Pokéballs, Potions e Dinheiro, e gera decisões prévias
para garantir a sobrevivência e prontidão do Klayton.

Exemplo:
- Se Pokéballs < 5 e o Goal for HUNT ➔ Insere meta prévia BUY_ITEMS (ShopSkill).
- Se HP < 20% ou Status != OK ➔ Insere meta prévia RETURN_TO_CENTER (HealSkill).

Autor: Klayton Companion Agent
Data: 2026-08-30
"""

from typing import Optional, Dict, Any
from ..world.world_state import WorldState
from .goal_engine import Goal
try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger("ResourceManager")


class ResourceManager:
    """
    Gerenciador de Recursos e Avaliação de Bom Senso de Sobrevivência.
    """

    def __init__(self, min_pokeballs: int = 5, min_potions: int = 2):
        self.min_pokeballs = min_pokeballs
        self.min_potions = min_potions

    def evaluate_resource_readiness(self, world: WorldState, target_goal: Goal) -> Goal:
        """
        Avalia se os recursos atuais são suficientes para iniciar o objetivo desejado.
        Caso contrário, redireciona o agente para um objetivo de preparação.
        """
        # 1. Checagem de Saúde (Prioridade Máxima)
        if world.team.needs_healing:
            logger.warning("🩹 Equipe precisa de cura! Redirecionando para HEAL_TEAM antes de prosseguir.")
            return Goal.HEAL_TEAM

        # 2. Checagem de Pokébolas para Caça ou Captura
        if target_goal in [Goal.HUNT, Goal.FISH] and world.resources.pokeballs_count < self.min_pokeballs:
            if world.resources.money >= 500:
                logger.warning(f"🎒 Pokéballs insuficientes ({world.resources.pokeballs_count} < {self.min_pokeballs}). Redirecionando para BUY_ITEMS.")
                return Goal.BUY_ITEMS
            else:
                logger.info("⚠️ Pokéballs insuficientes e sem saldo suficiente para comprar.")

        return target_goal
