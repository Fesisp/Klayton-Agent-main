"""
World Graph - Grafo de Navegação Espacial (A* / Dijkstra)
==========================================================

Mantém a topologia de nós e arestas do mundo, permitindo busca de menor caminho (shortest_path).

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

import heapq
from typing import Dict, List, Optional, Set, Tuple
from .world_node import WorldNode
from .world_edge import WorldEdge


class WorldGraph:
    """Grafo topológico de mapas e conexões."""

    def __init__(self):
        self.nodes: Dict[str, WorldNode] = {}
        self.edges: Dict[str, List[WorldEdge]] = {}
        self.blocked_edges: Set[Tuple[str, str]] = set()

    def add_node(self, node: WorldNode) -> None:
        self.nodes[node.id] = node
        if node.id not in self.edges:
            self.edges[node.id] = []

    def add_edge(self, edge: WorldEdge) -> None:
        if edge.source not in self.edges:
            self.edges[edge.source] = []
        self.edges[edge.source].append(edge)

        if edge.bidirectional:
            rev_edge = WorldEdge(
                source=edge.target,
                target=edge.source,
                cost=edge.cost,
                action=edge.action,
                bidirectional=True,
                requires_interaction=edge.requires_interaction,
                transition=edge.transition
            )
            if edge.target not in self.edges:
                self.edges[edge.target] = []
            self.edges[edge.target].append(rev_edge)

    def neighbors(self, node_id: str) -> List[Tuple[WorldNode, WorldEdge]]:
        result = []
        for edge in self.edges.get(node_id, []):
            if (edge.source, edge.target) in self.blocked_edges:
                continue
            target_node = self.nodes.get(edge.target)
            if target_node:
                result.append((target_node, edge))
        return result

    def shortest_path(self, source_id: str, target_id: str) -> Optional[List[str]]:
        """Calcula o menor caminho entre o nó de origem e o nó de destino via Dijkstra."""
        if source_id not in self.nodes or target_id not in self.nodes:
            return None

        if source_id == target_id:
            return [source_id]

        queue: List[Tuple[float, str, List[str]]] = [(0.0, source_id, [source_id])]
        visited: Set[str] = set()

        while queue:
            (cost, current, path) = heapq.heappop(queue)

            if current == target_id:
                return path

            if current in visited:
                continue
            visited.add(current)

            for neighbor_node, edge in self.neighbors(current):
                if neighbor_node.id not in visited:
                    heapq.heappush(queue, (cost + edge.cost, neighbor_node.id, path + [neighbor_node.id]))

        return None
