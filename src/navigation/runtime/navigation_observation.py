"""
Navigation Observation - Snapshot Imutável de Percepção de Navegação
======================================================================

Snapshot instantâneo e imutável dos elementos perceptuais espaciais.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass(frozen=True)
class NavigationObservation:
    """Snapshot perceptual instantâneo de navegação."""
    timestamp: float

    map_id: Optional[str] = None

    player_screen_x: Optional[float] = None
    player_screen_y: Optional[float] = None

    world_x: Optional[float] = None
    world_y: Optional[float] = None

    visible_landmarks: Tuple[str, ...] = ()

    transition_detected: bool = False

    movement_possible: Optional[bool] = None

    frame_signature: Optional[str] = None

    confidence: float = 0.0
