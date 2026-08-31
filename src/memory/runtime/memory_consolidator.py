"""
Memory Consolidator - Consolidação de Episódios em Fatos Semânticos
====================================================================

Analisa episódios recorrentes e os consolida em fatos semânticos quando atingem o limite de confirmações.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

import time
from typing import List, Optional
from .memory_record import MemoryRecord
from .memory_type import MemoryType
from .memory_admission import MemoryAdmissionPolicy
from .memory_store import MemoryStore


class MemoryConsolidator:
    """Consolidador de memória episódica para semântica."""

    def __init__(self, store: MemoryStore, policy: MemoryAdmissionPolicy = MemoryAdmissionPolicy()):
        self.store = store
        self.policy = policy

    def consolidate(self) -> List[MemoryRecord]:
        """Avalia episódios recentes e promove fatos com confirmações suficientes."""
        episodes = self.store.list_all_records(MemoryType.EPISODIC)
        key_counts = {}

        for ep in episodes:
            if ep.key not in key_counts:
                key_counts[ep.key] = []
            key_counts[ep.key].append(ep)

        promoted: List[MemoryRecord] = []
        now = time.time()

        for key, ep_list in key_counts.items():
            if len(ep_list) >= self.policy.semantic_min_confirmations:
                # Verifica se já existe o fato semântico
                existing = self.store.find_records_by_key(key, MemoryType.SEMANTIC)
                if not existing:
                    sample = ep_list[0]
                    fact_record = MemoryRecord(
                        type=MemoryType.SEMANTIC,
                        key=key,
                        value=sample.value,
                        confidence=0.90,
                        source=sample.source,
                        created_at=now,
                        updated_at=now,
                        observations=len(ep_list),
                        tags=sample.tags
                    )
                    if self.policy.allow_semantic_commit(fact_record):
                        self.store.save_record(fact_record)
                        promoted.append(fact_record)

        return promoted
