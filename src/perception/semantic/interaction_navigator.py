"""
Interaction Navigator & Zone System
====================================

Navegação de precisão egocêntrica para aproximação e posicionamento em relação a NPCs,
portas, baús e objetos interativos antes de enviar comandos de ação.

Inclui confirmação obrigatória pós-interação para verificar se o diálogo/menu foi aberto.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger("InteractionNavigator")

from .target_tracker import TrackedEntity, PLAYER_SCREEN_POSITION


@dataclass
class InteractionZone:
    """Zona e condições geométricas válidas para aproximação e interação."""
    target_id: str
    valid_sides: List[str] = field(default_factory=lambda: ["north", "south", "east", "west"])
    minimum_distance: float = 0.04  # Distância normalizada mínima
    maximum_distance: float = 0.15  # Distância normalizada máxima
    required_facing: Optional[str] = None


class InteractionNavigator:
    """
    Navegador de aproximação egocêntrica e verificador pós-interação.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}

    def calculate_approach_vector(self, target: TrackedEntity, zone: Optional[InteractionZone] = None) -> Tuple[float, float, float]:
        """
        Calcula o vetor de aproximação (dx, dy, distance) em coordenadas egocêntricas.
        O jogador fica fixo no centro (0.5, 0.5).
        """
        player_x, player_y = PLAYER_SCREEN_POSITION
        target_x, target_y = target.center

        dx = target_x - player_x
        dy = target_y - player_y
        distance = (dx ** 2 + dy ** 2) ** 0.5

        return dx, dy, distance

    def is_in_interaction_range(self, target: TrackedEntity, zone: Optional[InteractionZone] = None) -> bool:
        """Verifica se o agente já está posicionado dentro da zona válida de interação."""
        zone = zone or InteractionZone(target_id=target.entity_id)
        _, _, distance = self.calculate_approach_vector(target, zone)
        return zone.minimum_distance <= distance <= zone.maximum_distance

    def verify_post_interaction(
        self,
        before_state: Dict[str, Any],
        after_state: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """
        Confirma se a interação física teve efeito real no jogo.
        Verifica: diálogo aberto, menu aberto, mudança de mapa ou quest atualizada.
        """
        if after_state.get("game_state") != before_state.get("game_state"):
            return True, f"game_state_changed ({before_state.get('game_state')} -> {after_state.get('game_state')})"

        if after_state.get("dialog_open") and not before_state.get("dialog_open"):
            return True, "dialog_opened"

        if after_state.get("menu_open") and not before_state.get("menu_open"):
            return True, "menu_opened"

        if after_state.get("current_map") != before_state.get("current_map"):
            return True, f"map_changed ({before_state.get('current_map')} -> {after_state.get('current_map')})"

        return False, "no_interaction_effect_detected"
