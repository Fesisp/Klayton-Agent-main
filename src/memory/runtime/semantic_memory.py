"""
Semantic Memory - Fatos Aprendidos e Promovidos
==============================================

Armazena fatos consolidados e promovidos com alta confiança sobre o ambiente e o jogo.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

from typing import List, Optional
from .memory_record import MemoryRecord
from .memory_type import MemoryType
from .memory_store import MemoryStore


class SemanticMemory:
    """Gerenciador de memória semântica aprendida."""

    def __init__(self, store: MemoryStore):
        self.store = store

    def add_fact(self, record: MemoryRecord) -> None:
        record.type = MemoryType.SEMANTIC
        self.store.save_record(record)

    def get_fact(self, key: str) -> Optional[MemoryRecord]:
        records = self.store.find_records_by_key(key, MemoryType.SEMANTIC)
        if records:
            return records[0]
        return None

    def list_facts(self) -> List[MemoryRecord]:
        return self.store.list_all_records(MemoryType.SEMANTIC)
