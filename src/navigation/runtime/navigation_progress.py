"""
Navigation Progress - Classificação de Progresso Espacial
==========================================================

Enumeração contendo os estados formais de avanço em rotas.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

from enum import Enum


class NavigationProgress(Enum):
    """Classificação empírica do avanço na rota."""
    UNKNOWN = "unknown"
    NO_PROGRESS = "no_progress"
    PROGRESS = "progress"
    WAYPOINT_REACHED = "waypoint_reached"
    ARRIVED = "arrived"
    MAP_CHANGED = "map_changed"
    DEVIATED = "deviated"
    STUCK = "stuck"
