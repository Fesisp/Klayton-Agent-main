"""
Battle Skill - Máquina de Estados de Combate em Ciclo Fechado
============================================================

Executa o ciclo completo de batalha orientada a feedback:
ACQUIRE_STATE ➔ DECIDE ➔ EXECUTE ➔ VERIFY ➔ WAIT_NEXT_TURN ➔ COMPLETE

Autor: Klayton Companion Agent
Data: 2026-08-31
"""

from __future__ import annotations

import time
from enum import Enum
from typing import Any, Dict, Optional, List
try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger("BattleSkill")

from .base_skill import BaseSkill, SkillResult, SkillStatus
from ..world.world_state import WorldState
from ..battle.runtime.battle_observation import BattleObservation
from ..battle.runtime.battle_state_tracker import BattleStateTracker
from ..battle.runtime.battle_action import BattleAction, BattleActionType
from ..battle.runtime.battle_decision import BattleDecision
from ..battle.runtime.battle_action_executor import BattleActionExecutor
from ..battle.runtime.battle_outcome_verifier import BattleOutcomeVerifier, OutcomeStatus


class BattleSkillPhase(Enum):
    """Fases da máquina de estados em ciclo fechado da BattleSkill."""
    ACQUIRE_STATE = "acquire_state"
    DECIDE = "decide"
    EXECUTE = "execute"
    VERIFY = "verify"
    WAIT_NEXT_TURN = "wait_next_turn"
    COMPLETE = "complete"
    FAILED = "failed"


class BattleSkill(BaseSkill):
    """
    Skill autônoma de combate em ciclo fechado.
    """

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(name="BattleSkill", config=config)
        self.phase: BattleSkillPhase = BattleSkillPhase.ACQUIRE_STATE
        self.tracker: BattleStateTracker = BattleStateTracker()
        self.executor: BattleActionExecutor = BattleActionExecutor()
        self.verifier: BattleOutcomeVerifier = BattleOutcomeVerifier()

        self.current_decision: Optional[BattleDecision] = None
        self.before_obs: Optional[BattleObservation] = None
        self.after_observations: List[BattleObservation] = []

    def reset_runtime_state(self) -> None:
        super().reset_runtime_state()
        self.phase = BattleSkillPhase.ACQUIRE_STATE
        self.tracker = BattleStateTracker()
        self.executor.reset()
        self.current_decision = None
        self.before_obs = None
        self.after_observations = []

    def can_execute(self, world: WorldState) -> bool:
        return world.battle.in_battle or world.battle.is_shiny

    def execute(self, world: WorldState, components: Dict[str, Any]) -> SkillResult:
        strategy = components.get('strategy')
        input_sim = components.get('input')
        screen = components.get('screen')

        if not world.battle.in_battle and not world.battle.is_shiny:
            return SkillResult(status=SkillStatus.SUCCESS, message="Batalha concluída com sucesso")

        if world.battle.is_shiny:
            return SkillResult(status=SkillStatus.INTERRUPTED, message="Shiny encontrado! Ação pausada por segurança.")

        now = time.time()
        active_pkmn = world.team.active_pokemon.name if world.team.active_pokemon else (world.battle.player_pokemon or "PlayerPkmn")
        enemy_pkmn = world.battle.opponent_name or world.battle.enemy_pokemon or "EnemyPkmn"

        # Constrói observação a partir do WorldState atual
        current_obs = BattleObservation(
            timestamp=now,
            in_battle=world.battle.in_battle,
            player_pokemon=active_pkmn,
            enemy_pokemon=enemy_pkmn,
            player_hp_ratio=world.team.average_hp_percentage,
            enemy_hp_ratio=world.battle.opponent_hp_percentage,
            enemy_status=world.battle.opponent_status,
            move_menu_visible=True,
            confidence=0.90
        )

        events = self.tracker.update(current_obs)

        # 1. ACQUIRE_STATE / DECIDE
        if self.phase in [BattleSkillPhase.ACQUIRE_STATE, BattleSkillPhase.WAIT_NEXT_TURN]:
            self.before_obs = current_obs
            self.after_observations = []

            if strategy and hasattr(strategy, 'decide_action'):
                self.current_decision = strategy.decide_action(active_pkmn, enemy_pkmn, world=world)
            else:
                act = BattleAction(type=BattleActionType.MOVE, move_slot=0, reason="Default Move")
                self.current_decision = BattleDecision(action=act, score=0.8, confidence=0.8, reason="Default")

            self.executor.start(self.current_decision.action, current_obs)
            self.phase = BattleSkillPhase.EXECUTE

        # 2. EXECUTE (Envia input físico no jogo)
        if self.phase == BattleSkillPhase.EXECUTE:
            self.executor.tick(current_obs, input_sim, screen)
            self.phase = BattleSkillPhase.VERIFY

        # 3. VERIFY (Validação empírica de resultado)
        if self.phase == BattleSkillPhase.VERIFY:
            self.after_observations.append(current_obs)
            action = self.current_decision.action if self.current_decision else BattleAction(type=BattleActionType.MOVE, move_slot=0)

            outcome = self.verifier.verify(action, self.before_obs, self.after_observations, events)
            world.battle.last_action = action
            world.battle.last_outcome = outcome

            if outcome.status == OutcomeStatus.CONFIRMED:
                self.phase = BattleSkillPhase.WAIT_NEXT_TURN
                return SkillResult(
                    status=SkillStatus.RUNNING,
                    message=f"Batalha: Ação '{action.type.value}' confirmada por evidência no jogo!"
                )
            elif outcome.status in [OutcomeStatus.REJECTED, OutcomeStatus.TIMEOUT]:
                self.executor.reset()
                self.phase = BattleSkillPhase.DECIDE
                return SkillResult(
                    status=SkillStatus.RUNNING,
                    message=f"Batalha: Ação '{action.type.value}' reportou {outcome.status.value}. Reavaliando..."
                )

        return SkillResult(
            status=SkillStatus.RUNNING,
            message=f"Batalha: Executando combate contra {enemy_pkmn} ({active_pkmn})"
        )

    def is_complete(self, world: WorldState) -> bool:
        return not world.battle.in_battle
