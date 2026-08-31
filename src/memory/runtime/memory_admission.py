"""
Memory Admission Policy - Filtro de Admissão de Memória
========================================================

Filtra episódios e exige múltiplas confirmações (semantic_min_confirmations = 3) para promoção semântica.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

from dataclasses import dataclass
from .memory_record import MemoryRecord
from .provenance import EvidenceSource


@dataclass(frozen=True)
class MemoryAdmissionPolicy:
    """Política imutável de limites de admissão de memória."""
    episodic_min_confidence: float = 0.50
    semantic_candidate_min_confidence: float = 0.70
    semantic_commit_min_confidence: float = 0.85
    semantic_min_confirmations: int = 3

    def allow_episodic(self, record: MemoryRecord) -> bool:
        return record.confidence >= self.episodic_min_confidence

    def allow_semantic_candidate(self, record: MemoryRecord) -> bool:
        # OCR/VLM isolados nunca viram candidatos semânticos sem validação
        if record.source in [EvidenceSource.OCR, EvidenceSource.VLM, EvidenceSource.INFERRED]:
            return False
        return record.confidence >= self.semantic_candidate_min_confidence

    def allow_semantic_commit(self, record: MemoryRecord) -> bool:
        if record.source == EvidenceSource.USER_CONFIRMED:
            return True
        return record.observations >= self.semantic_min_confirmations and record.confidence >= self.semantic_commit_min_confidence
