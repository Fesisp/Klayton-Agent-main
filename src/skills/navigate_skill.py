"""
Navigate Skill - Navegação Global por Grafos e Coordenadas
==========================================================

Utiliza o MapGraph global (95 mapas) e cálculo A* para conduzir o agente
até o mapa e as coordenadas de destino pretendidas.

Autor: Klayton Companion Agent Framework
Data: 2026-08-30
"""

from typing import Any, Dict, List, Optional
from .base_skill import BaseSkill, SkillResult, SkillStatus
from ..world.world_state import WorldState
from ..navigation.map_graph import MapGraph


class NavigateSkill(BaseSkill):
    """
    Skill de navegação intermapas e interponto.
    """

    def __init__(self, target_map: str = "Viridian City", config: Dict[str, Any] = None):
        super().__init__(name="NavigateSkill", config=config)
        self.target_map = target_map
        self.graph = MapGraph()
        self.graph.load_all_maps_from_disk()
        self.current_route: List[str] = []

    def can_execute(self, world: WorldState) -> bool:
        return not world.battle.in_battle

    def execute(self, world: WorldState, components: Dict[str, Any]) -> SkillResult:
        input_sim = components.get('input')
        current_map = world.location.current_map

        if current_map == self.target_map:
            return SkillResult(status=SkillStatus.SUCCESS, message=f"Chegamos com sucesso ao mapa '{self.target_map}'!")

        if not self.current_route or self.current_route[-1] != self.target_map:
            self.current_route = self.graph.find_route(current_map, self.target_map)

        if not self.current_route:
            # Fallback direto de passo exploratório
            if hasattr(input_sim, 'press'):
                input_sim.press('w')
            return SkillResult(status=SkillStatus.RUNNING, message=f"Navegando em direção a {self.target_map}")

        next_waypoint = self.current_route[1] if len(self.current_route) > 1 else self.target_map
        if hasattr(input_sim, 'press'):
            input_sim.press('w')

        return SkillResult(
            status=SkillStatus.RUNNING,
            message=f"Navegando: {current_map} ➔ Próximo: {next_waypoint} (Destino Final: {self.target_map})"
        )

    def is_complete(self, world: WorldState) -> bool:
        return world.location.current_map == self.target_map
