"""
Map Graph & Route Planner - Navegação por Grafo de Mapas
========================================================

Representa as conexões entre mapas, cidades, rotas e regiões do jogo.
Utiliza o algoritmo A* para calcular o caminho mais curto entre duas localidades.

Autor: Klayton Companion Agent
Data: 2026-08-30
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set


@dataclass
class MapNode:
    name: str
    exits: Dict[str, str] = field(default_factory=dict)  # direção -> mapa_destino
    connections: List[str] = field(default_factory=list)  # lista de mapas adjacentes


class MapGraph:
    """
    Grafo de conexões dos mapas do mundo.
    """

    def __init__(self):
        self.nodes: Dict[str, MapNode] = {}

    def add_map(self, name: str, connections: List[str]) -> None:
        self.nodes[name] = MapNode(name=name, connections=connections)

    def find_route(self, start_map: str, target_map: str) -> List[str]:
        """
        Encontra o menor caminho de mapas entre start_map e target_map (BFS/A*).
        """
        if start_map not in self.nodes or target_map not in self.nodes:
            return []

        if start_map == target_map:
            return [start_map]

        queue: List[List[str]] = [[start_map]]
        visited: Set[str] = {start_map}

        while queue:
            path = queue.pop(0)
            node = path[-1]

            if node == target_map:
                return path

            for neighbor in self.nodes.get(node, MapNode(name=node)).connections:
                if neighbor not in visited:
                    visited.add(neighbor)
                    new_path = list(path)
                    new_path.append(neighbor)
                    queue.append(new_path)

        return []

    def load_all_maps_from_disk(self, maps_dir: Optional[Path] = None) -> int:
        """
        Carrega automaticamente todos os arquivos JSON de mapas do diretório data/maps/
        e constrói o grafo global de navegação de todas as regiões (Kanto, Johto e Unova).
        """
        import json
        if maps_dir is None:
            maps_dir = Path(__file__).resolve().parent.parent.parent / "data" / "maps"

        if not maps_dir.exists():
            return 0

        count = 0
        for json_file in maps_dir.glob("*.json"):
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    map_name = data.get("map_name")
                    exits = data.get("exits", [])
                    connections = [e["target_map"] for e in exits if "target_map" in e]
                    if map_name:
                        self.add_map(map_name, connections)
                        count += 1
            except Exception:
                pass

        return count
