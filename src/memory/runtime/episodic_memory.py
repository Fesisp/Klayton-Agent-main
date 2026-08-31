"""
Episodic Memory - Armazenamento de Episódios Históricos
======================================================

Gerencia o registro sequencial de observações, ações e eventos verificados.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

from typing import List, Optional
from .memory_record import MemoryRecord
from .memory_type import MemoryType
from .memory_store import MemoryStore


class EpisodicMemory:
    """Gerenciador de memória episódica."""

    def __init__(self, store: MemoryStore):
        self.store = store

    def add(self, record: MemoryRecord) -> None:
        record.type = MemoryType.EPISODIC
        self.store.save_record(record)

    def recent(self, limit: int = 50) -> List[MemoryRecord]:
        records = self.store.list_all_records(MemoryType.EPISODIC)
        records.sort(key=lambda r: r.created_at, reverse=True)
        return records[:limit]
