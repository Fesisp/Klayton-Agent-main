"""
Memory Facade - API Unificada de Memória e Aprendizado
=====================================================

Ponto único de entrada da camada de memória persistente do Klayton 2.0.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Set
from .runtime.memory_record import MemoryRecord
from .runtime.memory_type import MemoryType
from .runtime.provenance import EvidenceSource
from .runtime.memory_store import MemoryStore
from .runtime.episodic_memory import EpisodicMemory
from .runtime.semantic_memory import SemanticMemory
from .runtime.procedural_memory import ProceduralMemory
from .runtime.relationship_memory import RelationshipMemory
from .runtime.memory_retriever import MemoryRetriever
from .runtime.contradiction_resolver import ContradictionResolver
from .runtime.memory_consolidator import MemoryConsolidator


class MemoryFacade:
    """Façade unificada para acesso à memória persistente."""

    def __init__(self, store: Optional[MemoryStore] = None):
        self.store = store or MemoryStore()
        self.episodic = EpisodicMemory(self.store)
        self.semantic = SemanticMemory(self.store)
        self.procedural = ProceduralMemory(self.store)
        self.relationship = RelationshipMemory(self.store)

        self.retriever = MemoryRetriever(self.store)
        self.resolver = ContradictionResolver(self.store)
        self.consolidator = MemoryConsolidator(self.store)

    def record_episode(self, key: str, value: Any, source: EvidenceSource = EvidenceSource.DIRECT_OBSERVATION, confidence: float = 0.90, tags: Optional[Set[str]] = None) -> MemoryRecord:
        record = MemoryRecord(
            type=MemoryType.EPISODIC,
            key=key,
            value=value,
            confidence=confidence,
            source=source,
            tags=tags or set()
        )
        self.episodic.add(record)
        return record

    def record_fact_candidate(self, key: str, value: Any, source: EvidenceSource = EvidenceSource.INFERRED, confidence: float = 0.70) -> MemoryRecord:
        record = MemoryRecord(
            type=MemoryType.SEMANTIC,
            key=key,
            value=value,
            confidence=confidence,
            source=source
        )
        return self.resolver.resolve_and_save(record)

    def retrieve(self, query: Optional[str] = None, tags: Optional[Set[str]] = None, min_confidence: float = 0.0, limit: int = 20) -> List[MemoryRecord]:
        return self.retriever.retrieve(query=query, tags=tags, min_confidence=min_confidence, limit=limit)
