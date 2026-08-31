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

    def __init__(self, target_map: Optional[str] = None, config: Dict[str, Any] = None):
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

        # Se target_map não foi definido na inicialização, tenta resolver do atributo dinâmico ou world
        target = self.target_map or getattr(self, 'target_map', None)
        if not target:
            return SkillResult(status=SkillStatus.FAILED, message="NavigateSkill: NENHUM MAPA DESTINO FORNECIDO")

        if current_map == target:
            return SkillResult(status=SkillStatus.SUCCESS, message=f"Chegamos com sucesso ao mapa '{target}'!")

        if not self.current_route or self.current_route[-1] != target:
            self.current_route = self.graph.find_route(current_map, target)

        if not self.current_route:
            # Fallback direto de passo exploratório
            if hasattr(input_sim, 'press'):
                input_sim.press('w')
            return SkillResult(status=SkillStatus.RUNNING, message=f"Navegando em direção a {target}")

        next_waypoint = self.current_route[1] if len(self.current_route) > 1 else target
        if hasattr(input_sim, 'press'):
            input_sim.press('w')

        return SkillResult(
            status=SkillStatus.RUNNING,
            message=f"Navegando: {current_map} ➔ Próximo: {next_waypoint} (Destino Final: {target})"
        )

    def is_complete(self, world: WorldState) -> bool:
        target = self.target_map or getattr(self, 'target_map', None)
        if not target:
            return False
        return world.location.current_map == target
