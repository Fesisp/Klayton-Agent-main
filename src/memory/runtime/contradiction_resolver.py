"""
Contradiction Resolver - Resolução de Contradições em Memória
==============================================================

Detecta contradições entre registros antigos e novos, atualizando superseded_by sem exclusão silenciosa.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

import time
from typing import Optional
from .memory_record import MemoryRecord
from .memory_store import MemoryStore


class ContradictionResolver:
    """Resolvedor de contradições de memória."""

    def __init__(self, store: MemoryStore):
        self.store = store

    def resolve_and_save(self, new_record: MemoryRecord) -> Optional[MemoryRecord]:
        """
        Verifica se existe contradição com registros anteriores da mesma chave.
        Se existir contradição, o registro anterior é marcado com superseded_by.
        """
        existing_list = self.store.find_records_by_key(new_record.key, new_record.type)

        for old in existing_list:
            if old.value != new_record.value:
                # Contradição detectada! Se o novo registro tiver maior ou igual confiança, substitui.
                if new_record.confidence >= old.confidence:
                    old.superseded_by = new_record.id
                    old.updated_at = time.time()
                    self.store.save_record(old)

        self.store.save_record(new_record)
        return new_record
