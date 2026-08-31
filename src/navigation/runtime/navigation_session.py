"""
Navigation Session - Sessão Estruturada de Navegação
=====================================================

Armazena o histórico completo de rota, origem, destino, passos executados e resultado final.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from ...world.model.world_location import WorldLocation


@dataclass
class NavigationSession:
    """Sessão gravável de navegação para auditoria e replay."""
    id: str
    origin: Optional[Dict[str, Any]] = None
    destination: Optional[Dict[str, Any]] = None

    started_at: float = field(default_factory=time.time)
    ended_at: Optional[float] = None

    route_id: Optional[str] = None

    actions: List[Dict[str, Any]] = field(default_factory=list)
    observations: List[Dict[str, Any]] = field(default_factory=list)
    events: List[Dict[str, Any]] = field(default_factory=list)

    result: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.id,
            "origin": self.origin,
            "destination": self.destination,
            "started_at": self.started_at,
            "ended_at": self.ended_at,
            "route_id": self.route_id,
            "result": self.result,
            "actions": self.actions,
            "observations": self.observations,
            "events": self.events,
        }
