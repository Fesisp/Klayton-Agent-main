"""
Localization Engine - Motor de Localização por Hierarquia Estrita
===================================================================

Estima a localização atual do agente (WorldLocation) através de hierarquia estrita:
1. Coordenadas explícitas ➔ 2. Map ID + Posição local ➔ 3. Landmark ➔ 4. Temporal ➔ 5. Histórico ➔ 6. Fallback semântico.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

from typing import Optional
from .navigation_observation import NavigationObservation
from ...world.model.world_location import WorldLocation, LocationConfidence


class LocalizationEngine:
    """Motor de localização estruturada."""

    def locate(
        self,
        observation: NavigationObservation,
        previous_location: Optional[WorldLocation] = None
    ) -> WorldLocation:
        """
        Estima a localização atual utilizando a hierarquia perceptual.
        """
        # Level 1: Coordenadas mundiais explícitas
        if observation.world_x is not None and observation.world_y is not None:
            return WorldLocation(
                map_id=observation.map_id or (previous_location.map_id if previous_location else "Unknown"),
                x=observation.world_x,
                y=observation.world_y,
                confidence=LocationConfidence.HIGH
            )

        # Level 2: Map ID conhecido
        if observation.map_id:
            x_val = observation.player_screen_x if observation.player_screen_x is not None else (previous_location.x if previous_location else None)
            y_val = observation.player_screen_y if observation.player_screen_y is not None else (previous_location.y if previous_location else None)
            return WorldLocation(
                map_id=observation.map_id,
                x=x_val,
                y=y_val,
                confidence=LocationConfidence.MEDIUM
            )

        # Level 3: Landmark visual conhecido
        if observation.visible_landmarks:
            return WorldLocation(
                map_id=previous_location.map_id if previous_location else "Unknown",
                landmark=observation.visible_landmarks[0],
                confidence=LocationConfidence.MEDIUM
            )

        # Level 4: Manutenção temporal da localização anterior
        if previous_location and previous_location.confidence != LocationConfidence.UNKNOWN:
            return previous_location

        return WorldLocation(confidence=LocationConfidence.UNKNOWN)
