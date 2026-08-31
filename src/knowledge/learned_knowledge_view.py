"""
Learned Knowledge View - Visão Combinada de Conhecimento Canônico e Aprendido
=============================================================================

Agrega consultas aos bancos SQLite canônicos (data/knowledge/) e à memória semântica aprendida
sem sobrescrever arquivos de banco de dados canônicos.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

from typing import Any, Dict, Optional
from ..memory.memory_facade import MemoryFacade
from .knowledge_base import KnowledgeBase


class LearnedKnowledgeView:
    """Visão agregada de conhecimento canônico e memória aprendida."""

    def __init__(self, canonical_kb: Optional[KnowledgeBase] = None, memory_facade: Optional[MemoryFacade] = None):
        self.kb = canonical_kb or KnowledgeBase()
        self.memory = memory_facade or MemoryFacade()

    def get_pokemon_info(self, name: str) -> Optional[Dict[str, Any]]:
        """Consulta o banco canônico e enriquece com memórias semânticas aprendidas."""
        base_info = self.kb.get_pokemon_info(name)

        learned_records = self.memory.retrieve(query=f"pokemon_{name.lower()}", min_confidence=0.70)
        if learned_records and base_info is not None:
            base_info = dict(base_info)
            for rec in learned_records:
                if isinstance(rec.value, dict):
                    base_info.update(rec.value)

        return base_info
