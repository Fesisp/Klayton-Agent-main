"""
Memory Index - Indexador de Memória Persistente
==============================================

Indexador em memória para busca rápida por tipo, chave, tags e timestamps.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

from typing import Dict, List, Set
from .memory_record import MemoryRecord
from .memory_type import MemoryType


class MemoryIndex:
    """Indexador tático de registros de memória."""

    def __init__(self):
        self.by_key: Dict[str, List[MemoryRecord]] = {}
        self.by_tag: Dict[str, Set[str]] = {}

    def index(self, record: MemoryRecord) -> None:
        if record.key not in self.by_key:
            self.by_key[record.key] = []
        self.by_key[record.key].append(record)

        for tag in record.tags:
            if tag not in self.by_tag:
                self.by_tag[tag] = set()
            self.by_tag[tag].add(record.id)
