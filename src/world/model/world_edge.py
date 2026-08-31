"""
World Edge - Aresta de Conexão Espacial
=======================================

Representa uma conexão orientada entre dois nós do modelo de mundo.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class WorldEdge:
    """Aresta ponderada de transição entre nós."""
    source: str
    target: str

    cost: float = 1.0
    action: str = "walk"

    bidirectional: bool = True

    requires_interaction: bool = False
    transition: bool = False
