"""
World Model - Agregador de Modelo de Mundo
===========================================

Agrega o grafo espacial, mapas conhecidos, landmarks e pontos notáveis (lojas, centros pokémon, NPCs).

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

from typing import Dict, List, Optional
from .world_graph import WorldGraph
from .world_node import WorldNode
from .world_edge import WorldEdge
from .world_location import WorldLocation, LocationConfidence


class WorldModel:
    """Modelo de mundo agregador."""

    def __init__(self):
        self.graph: WorldGraph = WorldGraph()
        self.known_maps: Dict[str, dict] = {}
        self.landmarks: Dict[str, WorldLocation] = {}

    def add_location(self, node_id: str, map_id: str, x: Optional[float] = None, y: Optional[float] = None, kind: str = "generic", label: Optional[str] = None) -> WorldNode:
        node = WorldNode(id=node_id, map_id=map_id, x=x, y=y, kind=kind, label=label)
        self.graph.add_node(node)
        return node

    def add_connection(self, source_id: str, target_id: str, cost: float = 1.0, action: str = "walk", transition: bool = False) -> WorldEdge:
        edge = WorldEdge(source=source_id, target=target_id, cost=cost, action=action, transition=transition)
        self.graph.add_edge(edge)
        return edge

    def find_nodes_by_kind(self, kind: str, map_id: Optional[str] = None) -> List[WorldNode]:
        res = []
        for node in self.graph.nodes.values():
            if node.kind.lower() == kind.lower():
                if map_id is None or node.map_id.lower() == map_id.lower():
                    res.append(node)
        return res
