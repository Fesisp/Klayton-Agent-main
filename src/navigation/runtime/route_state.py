"""
Route State - Estado de Rota Espacial
=====================================

Armazena a sequência de nós planejados, o índice atual e os sinalizadores de conclusão, desvio ou replanejamento.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class RouteState:
    """Estado de rota espacial ativa."""
    route_id: str

    nodes: List[str] = field(default_factory=list)

    current_index: int = 0

    completed: bool = False
    invalidated: bool = False

    replans: int = 0

    def current_node(self) -> Optional[str]:
        if 0 <= self.current_index < len(self.nodes):
            return self.nodes[self.current_index]
        return None

    def advance(self) -> bool:
        if self.current_index < len(self.nodes) - 1:
            self.current_index += 1
            if self.current_index == len(self.nodes) - 1:
                self.completed = True
            return True
        else:
            self.completed = True
            return False
