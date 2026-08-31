"""
Teaching Interpreter - Intepretador de Ensinamentos Humanos
===========================================================

Converte frases explicativas do usuário ("esse NPC cura") em registros USER_CONFIRMED na MemoryFacade.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

from typing import Any, Dict, Optional
from ...memory.memory_facade import MemoryFacade
from ...memory.runtime.provenance import EvidenceSource


class TeachingInterpreter:
    """Interpretador de frases de ensino do usuário."""

    def __init__(self, memory_facade: Optional[MemoryFacade] = None):
        self.memory = memory_facade or MemoryFacade()

    def process_teaching(self, key: str, value: Any) -> Dict[str, Any]:
        """Salva o ensinamento humano como fato confirmado pelo usuário."""
        record = self.memory.record_fact_candidate(
            key=key,
            value=value,
            source=EvidenceSource.USER_CONFIRMED,
            confidence=0.98
        )
        return {
            "status": "fact_learned",
            "key": record.key,
            "value": record.value,
            "confidence": record.confidence,
            "source": record.source.value
        }
