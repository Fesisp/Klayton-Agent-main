"""
World Node - Nó Espacial do Modelo de Mundo
===========================================

Representa um ponto notável no espaço (tile, landmark, porta, warp, npc, ponto de cura, loja, entrada/saída).

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class WorldNode:
    """Nó estruturado no grafo do mundo."""
    id: str
    map_id: str

    x: Optional[float] = None
    y: Optional[float] = None

    kind: str = "generic"  # tile, landmark, door, warp, npc, healing_point, shop, route_entry, route_exit
    label: Optional[str] = None
