"""
Battle State Tracker - Rastreamento Temporal e Detecção de Eventos de Combate
=============================================================================

Compara observações sequenciais de combate (previous vs current) e gera uma lista
de eventos empíricos (BattleEvent) com tolerância matemática a ruídos (HP_CHANGE_EPSILON).

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

import time
from typing import List, Optional
from .battle_observation import BattleObservation
from .battle_event import BattleEvent, BattleEventType

HP_CHANGE_EPSILON = 0.015


class BattleStateTracker:
    """Rastreador de estado de batalha e gerador de eventos empíricos."""

    def __init__(self):
        self.previous: Optional[BattleObservation] = None
        self.current: Optional[BattleObservation] = None
        self.turn_id: int = 0

    def update(self, observation: BattleObservation) -> List[BattleEvent]:
        events: List[BattleEvent] = []

        previous = self.current
        self.previous = previous
        self.current = observation

        now = observation.timestamp or time.time()

        # 1. Início ou Término de Batalha
        if previous is None or not previous.in_battle:
            if observation.in_battle:
                self.turn_id = 1
                events.append(BattleEvent(
                    type=BattleEventType.BATTLE_STARTED,
                    timestamp=now,
                    data={"enemy_pokemon": observation.enemy_pokemon, "player_pokemon": observation.player_pokemon},
                    confidence=observation.confidence
                ))
                events.append(BattleEvent(
                    type=BattleEventType.TURN_STARTED,
                    timestamp=now,
                    data={"turn_id": self.turn_id},
                    confidence=observation.confidence
                ))
            return events

        if previous.in_battle and not observation.in_battle:
            if previous.enemy_hp_ratio is not None and previous.enemy_hp_ratio <= 0.50:
                events.append(BattleEvent(
                    type=BattleEventType.ENEMY_FAINTED,
                    timestamp=now,
                    data={"enemy_pokemon": previous.enemy_pokemon},
                    confidence=0.95
                ))
                events.append(BattleEvent(
                    type=BattleEventType.BATTLE_WON,
                    timestamp=now,
                    data={"enemy_pokemon": previous.enemy_pokemon},
                    confidence=0.95
                ))
            events.append(BattleEvent(
                type=BattleEventType.BATTLE_ENDED,
                timestamp=now,
                data={"last_turn": self.turn_id},
                confidence=observation.confidence
            ))
            return events

        # 2. Detecção de Mudança de HP do Adversário
        if previous.enemy_hp_ratio is not None and observation.enemy_hp_ratio is not None:
            enemy_delta = observation.enemy_hp_ratio - previous.enemy_hp_ratio
            if abs(enemy_delta) >= HP_CHANGE_EPSILON:
                events.append(BattleEvent(
                    type=BattleEventType.ENEMY_HP_CHANGED,
                    timestamp=now,
                    data={"before": previous.enemy_hp_ratio, "after": observation.enemy_hp_ratio, "delta": enemy_delta},
                    confidence=observation.confidence
                ))

                # Faint do adversário
                if previous.enemy_hp_ratio > 0.02 and observation.enemy_hp_ratio <= 0.02:
                    events.append(BattleEvent(
                        type=BattleEventType.ENEMY_FAINTED,
                        timestamp=now,
                        data={"enemy_pokemon": previous.enemy_pokemon},
                        confidence=0.95
                    ))
                    events.append(BattleEvent(
                        type=BattleEventType.BATTLE_WON,
                        timestamp=now,
                        data={"enemy_pokemon": previous.enemy_pokemon},
                        confidence=0.95
                    ))

        # 3. Detecção de Mudança de HP do Jogador
        if previous.player_hp_ratio is not None and observation.player_hp_ratio is not None:
            player_delta = observation.player_hp_ratio - previous.player_hp_ratio
            if abs(player_delta) >= HP_CHANGE_EPSILON:
                events.append(BattleEvent(
                    type=BattleEventType.PLAYER_HP_CHANGED,
                    timestamp=now,
                    data={"before": previous.player_hp_ratio, "after": observation.player_hp_ratio, "delta": player_delta},
                    confidence=observation.confidence
                ))

                # Faint do jogador
                if previous.player_hp_ratio > 0.02 and observation.player_hp_ratio <= 0.02:
                    events.append(BattleEvent(
                        type=BattleEventType.PLAYER_FAINTED,
                        timestamp=now,
                        data={"player_pokemon": previous.player_pokemon},
                        confidence=0.95
                    ))

        # 4. Detecção de Troca de Pokémon do Jogador
        if previous.player_pokemon and observation.player_pokemon:
            if previous.player_pokemon.lower() != observation.player_pokemon.lower():
                events.append(BattleEvent(
                    type=BattleEventType.PLAYER_SWITCHED,
                    timestamp=now,
                    data={"before": previous.player_pokemon, "after": observation.player_pokemon},
                    confidence=0.95
                ))

        # 5. Detecção de Mudança de Status
        if previous.enemy_status != observation.enemy_status and observation.enemy_status is not None:
            events.append(BattleEvent(
                type=BattleEventType.ENEMY_STATUS_CHANGED,
                timestamp=now,
                data={"before": previous.enemy_status, "after": observation.enemy_status},
                confidence=0.90
            ))

        if previous.player_status != observation.player_status and observation.player_status is not None:
            events.append(BattleEvent(
                type=BattleEventType.PLAYER_STATUS_CHANGED,
                timestamp=now,
                data={"before": previous.player_status, "after": observation.player_status},
                confidence=0.90
            ))

        # 6. Transição de Turno (quando os menus reaparecem após ação)
        if not previous.move_menu_visible and observation.move_menu_visible:
            self.turn_id += 1
            events.append(BattleEvent(
                type=BattleEventType.TURN_STARTED,
                timestamp=now,
                data={"turn_id": self.turn_id},
                confidence=0.95
            ))

        return events
