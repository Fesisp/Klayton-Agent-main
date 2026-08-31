"""
Battle Session - Representação Estruturada de uma Sessão de Combate
===================================================================

Armazena o histórico completo de turnos, decisões, ações, observações e eventos de uma batalha.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class BattleSession:
    """Sessão completa de combate gravável para auditoria e replay."""
    id: str
    started_at: float = field(default_factory=time.time)
    ended_at: Optional[float] = None

    enemy_name: Optional[str] = None

    decisions: List[Dict[str, Any]] = field(default_factory=list)
    actions: List[Dict[str, Any]] = field(default_factory=list)
    observations: List[Dict[str, Any]] = field(default_factory=list)
    events: List[Dict[str, Any]] = field(default_factory=list)

    result: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.id,
            "started_at": self.started_at,
            "ended_at": self.ended_at,
            "enemy_name": self.enemy_name,
            "result": self.result,
            "decisions": self.decisions,
            "actions": self.actions,
            "observations": self.observations,
            "events": self.events,
        }
