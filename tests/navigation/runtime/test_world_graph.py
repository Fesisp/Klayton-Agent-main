"""
Test World Graph - Grafo Espacial e Algoritmo de Menor Caminho
=============================================================

Valida:
1. Inserção de nós e arestas bidirecionadas no WorldGraph.
2. Cálculo de menor caminho via algoritmo Dijkstra (shortest_path).

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.world.model.world_graph import WorldGraph
from src.world.model.world_node import WorldNode
from src.world.model.world_edge import WorldEdge


def test_world_graph_pathfinding():
    print("🧪 Testando WorldGraph (Pathfinding Dijkstra)...")

    graph = WorldGraph()
    n1 = WorldNode(id="A", map_id="MapA")
    n2 = WorldNode(id="B", map_id="MapB")
    n3 = WorldNode(id="C", map_id="MapC")

    graph.add_node(n1)
    graph.add_node(n2)
    graph.add_node(n3)

    graph.add_edge(WorldEdge(source="A", target="B", cost=1.0))
    graph.add_edge(WorldEdge(source="B", target="C", cost=2.0))

    path = graph.shortest_path("A", "C")
    assert path == ["A", "B", "C"]
    print(f"  ✅ Menor caminho calculado com sucesso: {' ➔ '.join(path)}")


if __name__ == "__main__":
    test_world_graph_pathfinding()
