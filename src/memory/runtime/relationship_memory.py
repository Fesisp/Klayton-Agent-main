"""
Relationship Memory - Preferências e Correções do Usuário
=========================================================

Gerencia instruções persistentes, preferências de interação e correções fornecidas pelo usuário.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

from typing import List, Optional
from .memory_record import MemoryRecord
from .memory_type import MemoryType
from .provenance import EvidenceSource
from .memory_store import MemoryStore


class RelationshipMemory:
    """Gerenciador de memória de relacionamento e preferências."""

    def __init__(self, store: MemoryStore):
        self.store = store

    def set_preference(self, key: str, value: str, confidence: float = 0.98) -> MemoryRecord:
        record = MemoryRecord(
            type=MemoryType.RELATIONSHIP,
            key=key,
            value=value,
            confidence=confidence,
            source=EvidenceSource.USER_CONFIRMED
        )
        self.store.save_record(record)
        return record

    def get_preference(self, key: str) -> Optional[MemoryRecord]:
        records = self.store.find_records_by_key(key, MemoryType.RELATIONSHIP)
        if records:
            return records[0]
        return None
