"""
Navigation Action - Ação Estruturada de Navegação Espacial
===========================================================

Representa comandos de movimento ou interação física (MOVE, INTERACT, TRANSITION, WAIT, REORIENT).

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class NavigationActionType(Enum):
    """Tipos de ações de navegação espacial."""
    MOVE = "move"
    INTERACT = "interact"
    TRANSITION = "transition"
    WAIT = "wait"
    REORIENT = "reorient"


@dataclass(frozen=True)
class NavigationAction:
    """Ação tática de movimento ou interação no mapa."""
    type: NavigationActionType

    direction: Optional[str] = None
    duration_ms: Optional[int] = None

    target_node: Optional[str] = None
    target_map: Optional[str] = None

    reason: Optional[str] = None
