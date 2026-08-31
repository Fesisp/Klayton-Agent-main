"""
Destination Resolver - Resolução de Metas Espaciais
===================================================

Converte metas abstratas (NPC, shop, healing_point, landmark, nome de cidade) em instâncias formais de WorldLocation.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

from typing import Any, Optional, Union
from ...world.model.world_location import WorldLocation, LocationConfidence
from ...world.model.world_model import WorldModel


class DestinationResolver:
    """Resolvedor de metas em localizações formais do modelo de mundo."""

    def resolve(self, target: Union[str, WorldLocation], world_model: Optional[WorldModel] = None) -> WorldLocation:
        """Converte uma meta abstrata ou texto em WorldLocation."""
        if isinstance(target, WorldLocation):
            return target

        target_str = str(target).strip()

        # Busca por nós notáveis no modelo de mundo (ex: healing_point, shop)
        if world_model:
            nodes = world_model.find_nodes_by_kind(target_str)
            if nodes:
                node = nodes[0]
                return WorldLocation(
                    map_id=node.map_id,
                    x=node.x,
                    y=node.y,
                    landmark=node.label or node.id,
                    confidence=LocationConfidence.HIGH
                )

        return WorldLocation(
            map_id=target_str,
            landmark=target_str,
            confidence=LocationConfidence.MEDIUM
        )
