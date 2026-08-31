"""
Memory Retriever - Mecanismo de Busca e Ranking de Memória
===========================================================

Realiza busca por termos, tags e limite de confiança com ranking ponderado:
score = relevance * confidence * recency_factor * source_weight

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

import time
from typing import List, Optional, Set
from .memory_record import MemoryRecord
from .memory_type import MemoryType
from .memory_store import MemoryStore


class MemoryRetriever:
    """Mecanismo de busca e ranking ponderado de memória."""

    def __init__(self, store: MemoryStore):
        self.store = store

    def retrieve(
        self,
        query: Optional[str] = None,
        tags: Optional[Set[str]] = None,
        min_confidence: float = 0.0,
        limit: int = 20
    ) -> List[MemoryRecord]:
        """Recupera e ordena registros por relevância e confiança."""
        records = self.store.list_all_records()
        filtered: List[MemoryRecord] = []

        now = time.time()

        for rec in records:
            if rec.confidence < min_confidence:
                continue

            if tags and not tags.issubset(rec.tags):
                continue

            if query and query.lower() not in rec.key.lower():
                continue

            filtered.append(rec)

        # Ranking: confidence * recency
        def score(r: MemoryRecord) -> float:
            age_hours = max(0.1, (now - r.updated_at) / 3600.0)
            recency = 1.0 / (1.0 + 0.05 * age_hours)
            return r.confidence * recency

        filtered.sort(key=score, reverse=True)
        return filtered[:limit]
