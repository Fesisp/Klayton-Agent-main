"""
Navigation System - Sistema Duplo de Navegação (Local + Global)
================================================================

Unifica:
1. Navegação Local: Desvio de obstáculos dentro do mesmo mapa via MovementVerifier.
2. Navegação Global: Roteamento A* entre cidades e rotas via MapGraph.
3. APIs Abstratas de Movimento: Navegação por posições, mapas, acompanhamento e descolamento.

Autor: Klayton Companion Agent
Data: 2026-08-30
"""

from typing import List, Optional, Tuple
from .map_graph import MapGraph
from .movement_verifier import MovementVerifier
from ..world.world_state import WorldState


class NavigationSystem:
    """
    Sistema Unificado de Navegação do Klayton Companion Agent.
    """

    def __init__(self):
        self.global_graph: MapGraph = MapGraph()
        self.global_graph.load_all_maps_from_disk()
        if len(self.global_graph.nodes) == 0:
            self._setup_default_kanto_graph()
        self.local_verifier: MovementVerifier = MovementVerifier(max_stuck_attempts=3)

    def _setup_default_kanto_graph(self) -> None:
        """Inicializa o mapa padrão de Kanto."""
        self.global_graph.add_map("Pallet Town", ["Route 1"])
        self.global_graph.add_map("Route 1", ["Pallet Town", "Viridian City"])
        self.global_graph.add_map("Viridian City", ["Route 1", "Route 2", "Viridian Forest"])
        self.global_graph.add_map("Viridian Forest", ["Viridian City", "Pewter City"])
        self.global_graph.add_map("Pewter City", ["Viridian Forest", "Route 3"])
        self.global_graph.add_map("Route 3", ["Pewter City", "Mt Moon"])
        self.global_graph.add_map("Mt Moon", ["Route 3", "Route 4"])
        self.global_graph.add_map("Route 4", ["Mt Moon", "Cerulean City"])

    def plan_global_route(self, current_map: str, target_map: str) -> List[str]:
        """Calcula rota global entre dois mapas."""
        return self.global_graph.find_route(current_map, target_map)

    def navigate_to_map(self, current_map: str, target_map: str) -> List[str]:
        """API Abstrata: Retorna o caminho de navegação entre mapas."""
        return self.plan_global_route(current_map, target_map)

    def navigate_to_position(self, target_pos: Tuple[int, int]) -> bool:
        """API Abstrata: Desloca o agente até as coordenadas relativas/absolutas."""
        return True

    def follow_player(self, player_pos: Optional[Tuple[int, int]] = None) -> bool:
        """API Abstrata: Mantém o agente próximo às coordenadas do líder."""
        return True

    def regroup_with_player(self) -> bool:
        """API Abstrata: Teleporta/Reagrupa o agente junto ao líder."""
        return True

    def recover_from_stuck(self) -> bool:
        """API Abstrata: Executa manobra de descolamento de obstáculo."""
        self.local_verifier.reset()
        return True

    def transition_map(self, direction: str) -> bool:
        """API Abstrata: Transiciona a porta/warp na direção especificada."""
        return True

    def verify_local_step(self, current_pos: Tuple[int, int]) -> bool:
        """Verifica se o último passo local se moveu ou se colidiu em obstáculo."""
        return self.local_verifier.verify(current_pos)

    def resolve_relative_position(self, landmark_description: str, world: WorldState) -> str:
        """
        Navegação Relativa (Fase 3 do Roadmap):
        Resolve a posição aproximada do agente a partir de descrições e pontos de referência sem coordenadas exatas.
        Ex: "perto do Pokémon Center", "seguindo direção do líder", "metade sul do mapa".
        """
        desc_clean = landmark_description.lower()
        if "pokemon center" in desc_clean or "centro" in desc_clean:
            world.location.important_landmarks.append("Pokemon Center")
            return "Aproximando-se do Pokémon Center mais próximo"
        elif "norte" in desc_clean or "north" in desc_clean:
            return "Deslocando na direção Norte do líder"
        elif "sul" in desc_clean or "south" in desc_clean:
            return "Deslocando na direção Sul do líder"
        elif "água" in desc_clean or "water" in desc_clean:
            return "Localizado próximo à borda de água"

        return f"Deslocando relativo ao ponto de referência: '{landmark_description}'"

    @property
    def is_stuck(self) -> bool:
        return self.local_verifier.is_stuck

    def reset_local(self) -> None:
        self.local_verifier.reset()
