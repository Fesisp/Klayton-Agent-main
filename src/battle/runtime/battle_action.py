"""
Battle Action - Ação Estruturada de Combate
==========================================

Representa uma ação tática abstrata e estruturada no runtime de batalha.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class BattleActionType(Enum):
    """Tipos de ações táticas em combate."""
    MOVE = "move"
    SWITCH = "switch"
    ITEM = "item"
    RUN = "run"
    CAPTURE = "capture"


@dataclass(frozen=True)
class BattleAction:
    """Ação tática de batalha estruturada."""
    type: BattleActionType

    move_name: Optional[str] = None
    move_slot: Optional[int] = None

    switch_target: Optional[str] = None
    switch_slot: Optional[int] = None

    item_name: Optional[str] = None

    reason: Optional[str] = None
