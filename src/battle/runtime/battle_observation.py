"""
Battle Observation - Dataclass Imutável de Percepção de Batalha
===============================================================

Representa a observação perceptual instantânea e imutável do estado de batalha.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class BattleObservation:
    """Snapshot instantâneo e imutável de uma observação de combate."""
    timestamp: float

    in_battle: bool

    player_pokemon: Optional[str] = None
    enemy_pokemon: Optional[str] = None

    player_hp_ratio: Optional[float] = None
    enemy_hp_ratio: Optional[float] = None

    player_status: Optional[str] = None
    enemy_status: Optional[str] = None

    player_level: Optional[int] = None
    enemy_level: Optional[int] = None

    move_menu_visible: bool = False
    pokemon_menu_visible: bool = False
    bag_menu_visible: bool = False
    run_button_visible: bool = False

    battle_text: Optional[str] = None

    confidence: float = 0.0
