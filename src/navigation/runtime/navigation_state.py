"""
Navigation State - Estado do Motor de Navegação
================================================

Estado ativo de navegação contendo localização atual, destino, rota e indicadores de stuck/desvio.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional
from ...world.model.world_location import WorldLocation, LocationConfidence


@dataclass
class NavigationState:
    """Estado do motor de navegação mantido no WorldState."""
    current_location: WorldLocation = field(default_factory=lambda: WorldLocation(confidence=LocationConfidence.UNKNOWN))
    destination: Optional[WorldLocation] = None

    route_id: Optional[str] = None
    route_progress: float = 0.0

    moving: bool = False
    stuck: bool = False
    deviated: bool = False

    last_progress_at: Optional[float] = None

    confidence: float = 0.0
