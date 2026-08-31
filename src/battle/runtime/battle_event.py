"""
Battle Event - Eventos Empíricos Observados em Combate
======================================================

Define os tipos de eventos empíricos detectados durante a transição entre observações de batalha.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict


class BattleEventType(Enum):
    """Tipos de eventos empíricos observáveis em combate."""
    BATTLE_STARTED = "battle_started"
    TURN_STARTED = "turn_started"

    PLAYER_ATTACKED = "player_attacked"
    ENEMY_ATTACKED = "enemy_attacked"

    PLAYER_HP_CHANGED = "player_hp_changed"
    ENEMY_HP_CHANGED = "enemy_hp_changed"

    PLAYER_STATUS_CHANGED = "player_status_changed"
    ENEMY_STATUS_CHANGED = "enemy_status_changed"

    PLAYER_SWITCHED = "player_switched"
    ENEMY_SWITCHED = "enemy_switched"

    PLAYER_FAINTED = "player_fainted"
    ENEMY_FAINTED = "enemy_fainted"

    CAPTURE_SUCCEEDED = "capture_succeeded"
    CAPTURE_FAILED = "capture_failed"

    BATTLE_WON = "battle_won"
    BATTLE_LOST = "battle_lost"
    BATTLE_ENDED = "battle_ended"

    ACTION_REJECTED = "action_rejected"
    UNKNOWN_CHANGE = "unknown_change"


@dataclass(frozen=True)
class BattleEvent:
    """Evento empírico detectado entre observações."""
    type: BattleEventType
    timestamp: float
    data: Dict[str, Any]
    confidence: float = 1.0
