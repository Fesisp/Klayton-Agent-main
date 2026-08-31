"""
Battle Perception - Agregador Perceptual de Batalha
===================================================

Combina HPBarReader, BattleOCR, GameStateDetector e buscas semânticas
para gerar uma instância imutável de BattleObservation.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

import time
from typing import Any, Optional
from ...battle.runtime.battle_observation import BattleObservation
from .hp_bar_reader import HPBarReader
from .battle_ocr import BattleOCR


class BattlePerception:
    """Agregador perceptual especializado de combate."""

    def __init__(self, game_state_detector: Any = None, ocr_engine: Any = None):
        self.detector = game_state_detector
        self.hp_reader = HPBarReader()
        self.battle_ocr = BattleOCR(ocr_engine)

    def observe(self, frame: Any, current_state: Optional[str] = None) -> BattleObservation:
        """Produz uma observação estruturada de combate a partir da captura da tela."""
        now = time.time()
        in_battle = (current_state == "IN_BATTLE") or (self.detector and getattr(self.detector, 'in_battle', False))

        if not in_battle:
            return BattleObservation(
                timestamp=now,
                in_battle=False,
                confidence=0.95
            )

        player_hp_ratio, p_conf = self.hp_reader.read_ratio(frame, {"type": "player"})
        enemy_hp_ratio, e_conf = self.hp_reader.read_ratio(frame, {"type": "enemy"})

        return BattleObservation(
            timestamp=now,
            in_battle=True,
            player_hp_ratio=player_hp_ratio,
            enemy_hp_ratio=enemy_hp_ratio,
            move_menu_visible=True,
            confidence=max(p_conf, e_conf, 0.80)
        )
