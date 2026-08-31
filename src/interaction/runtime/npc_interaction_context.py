"""
NPC Interaction Context - Contexto e Estado de Interação com NPC
================================================================

Estrutura imutável para rastreamento de diálogos e classificação empírica de papéis de NPCs.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class NPCInteractionContext:
    """Contexto imutável de interação com NPC."""
    npc_id: Optional[str] = None
    npc_name: Optional[str] = None

    map_id: Optional[str] = None
    dialogue_text: Optional[str] = None

    interaction_count: int = 0
    known_role: Optional[str] = None

    confidence: float = 0.0
