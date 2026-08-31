"""
Battle Skill - Capacidade Modular de Combate (Conexão com BattleStrategy e InputSimulator)
========================================================================================

Executa a pipeline de batalha do Klayton conectando o cérebro decisório à execução tática.

Autor: Klayton Companion Agent
Data: 2026-08-30
"""

import time
from typing import Any, Dict
try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger("BattleSkill")

from .base_skill import BaseSkill, SkillResult, SkillStatus
from ..world.world_state import WorldState


class BattleSkill(BaseSkill):
    """
    Skill autônoma de combate orientada a TTK, resistências e seleção de golpes.
    """

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(name="BattleSkill", config=config)

    def can_execute(self, world: WorldState) -> bool:
        return world.battle.in_battle or world.battle.is_shiny

    def execute(self, world: WorldState, components: Dict[str, Any]) -> SkillResult:
        strategy = components.get('strategy')
        input_sim = components.get('input')
        team_mgr = components.get('team_mgr')
        screen = components.get('screen')

        if not strategy or not input_sim:
            return SkillResult(status=SkillStatus.FAILED, message="Componentes ausentes (strategy ou input)")

        # Prioridade máxima: Shiny detectado
        if world.battle.is_shiny:
            return SkillResult(status=SkillStatus.INTERRUPTED, message="Shiny encontrado! Ação pausada por segurança.")

        if not world.battle.in_battle and not world.battle.is_shiny:
            return SkillResult(status=SkillStatus.SUCCESS, message="Batalha concluída com sucesso")

        active_pkmn = world.team.active_pokemon.name if world.team.active_pokemon else "PlayerPkmn"
        enemy_pkmn = world.battle.opponent_name or "EnemyPkmn"

        # 1. Consulta o melhor plano tático da BattleStrategy
        best_action = "ATTACK"
        if hasattr(strategy, 'get_best_action'):
            try:
                best_action = strategy.get_best_action(active_pkmn, enemy_pkmn)
            except Exception:
                best_action = "ATTACK"

        # 2. Executa a ação tática física no jogo
        if best_action in ["SWITCH_TO_RESISTANT", "SWITCH_MANDATORY"]:
            # Executa troca tática
            if hasattr(input_sim, 'click_pokemon_button') and screen:
                img = screen.capture() if hasattr(screen, 'capture') else None
                input_sim.click_pokemon_button(img)
            return SkillResult(
                status=SkillStatus.RUNNING,
                message=f"Batalha: Executando troca tática defensiva contra {enemy_pkmn}"
            )

        # 3. Execução de ataque ideal (Melhor TTK / Eficiência)
        best_slot = 0
        if hasattr(strategy, 'get_best_move'):
            try:
                best_slot = strategy.get_best_move(active_pkmn, enemy_pkmn)
            except Exception:
                best_slot = 0

        if best_slot == -1:
            best_slot = 0

        # Clica no slot de ataque escolhido
        if hasattr(input_sim, 'humanized_click_in_slot'):
            input_sim.humanized_click_in_slot(best_slot)
        elif hasattr(input_sim, 'click_in_slot'):
            input_sim.click_in_slot(best_slot)
        elif hasattr(input_sim, 'press'):
            input_sim.press('1')

        return SkillResult(
            status=SkillStatus.RUNNING,
            message=f"Batalha: {active_pkmn} atacou {enemy_pkmn} usando golpe do slot {best_slot} (Tática: {best_action})"
        )

    def is_complete(self, world: WorldState) -> bool:
        return not world.battle.in_battle
