"""
Navigation Progress Verifier - Verificador Empírico de Progresso Espacial
========================================================================

Verifica se uma ação de movimento resultou em progresso espacial (distance >= minimum_progress_distance,
transição de mapa ou chegada ao destino).

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

import math
from typing import List, Optional
from .navigation_action import NavigationAction, NavigationActionType
from .navigation_progress import NavigationProgress
from .route_state import RouteState
from ...world.model.world_location import WorldLocation


class NavigationProgressVerifier:
    """Validador empírico de progresso em navegação."""

    def __init__(self, minimum_progress_distance: float = 0.5):
        self.minimum_progress_distance = minimum_progress_distance

    def verify(
        self,
        before: Optional[WorldLocation],
        action: NavigationAction,
        after: Optional[WorldLocation],
        route_state: Optional[RouteState] = None,
        destination: Optional[WorldLocation] = None
    ) -> NavigationProgress:
        """
        Avalia o avanço empírico entre as localizações (before vs after).
        """
        if after is None or before is None:
            return NavigationProgress.UNKNOWN

        # 1. Chegada ao destino
        if destination:
            if destination.map_id and after.map_id and destination.map_id.lower() == after.map_id.lower():
                if destination.x is not None and after.x is not None and destination.y is not None and after.y is not None:
                    dist_dest = math.hypot(after.x - destination.x, after.y - destination.y)
                    if dist_dest <= 1.0:
                        return NavigationProgress.ARRIVED
                elif destination.landmark and after.landmark and destination.landmark.lower() in after.landmark.lower():
                    return NavigationProgress.ARRIVED

        # 2. Transição de mapa
        if before.map_id and after.map_id and before.map_id.lower() != after.map_id.lower():
            return NavigationProgress.MAP_CHANGED

        # 3. Verificação por Coordenadas
        if before.x is not None and before.y is not None and after.x is not None and after.y is not None:
            dist = math.hypot(after.x - before.x, after.y - before.y)
            if dist >= self.minimum_progress_distance:
                # Checa se alcançou waypoint da rota
                if route_state and route_state.current_node():
                    curr_node = route_state.current_node()
                    if after.map_id and curr_node and curr_node.lower() in after.map_id.lower():
                        return NavigationProgress.WAYPOINT_REACHED
                return NavigationProgress.PROGRESS
            else:
                return NavigationProgress.NO_PROGRESS

        # 4. Verificação por Landmark
        if before.landmark != after.landmark and after.landmark is not None:
            return NavigationProgress.PROGRESS

        if action.type == NavigationActionType.MOVE:
            return NavigationProgress.NO_PROGRESS

        return NavigationProgress.UNKNOWN
