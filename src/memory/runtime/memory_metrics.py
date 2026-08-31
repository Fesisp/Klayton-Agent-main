"""
Memory Metrics - Métricas Estatísticas de Memória e Aprendizado
================================================================

Calcula a taxa de aprendizado verificado (Verified Learning Rate) e a taxa de contradição (Contradiction Rate).

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class MemoryMetrics:
    """Calculador de métricas de memória."""
    episodes_recorded: int = 0
    semantic_candidates: int = 0
    semantic_promotions: int = 0
    contradictions_detected: int = 0
    records_superseded: int = 0
    retrievals: int = 0

    @property
    def verified_learning_rate(self) -> float:
        """verified_promotions / semantic_candidates."""
        if self.semantic_candidates == 0:
            return 0.0
        return self.semantic_promotions / self.semantic_candidates

    @property
    def contradiction_rate(self) -> float:
        """contradictions / semantic_updates."""
        if self.semantic_promotions == 0:
            return 0.0
        return self.contradictions_detected / self.semantic_promotions

    def to_dict(self) -> Dict[str, Any]:
        return {
            "episodes_recorded": self.episodes_recorded,
            "semantic_candidates": self.semantic_candidates,
            "semantic_promotions": self.semantic_promotions,
            "verified_learning_rate": self.verified_learning_rate,
            "contradictions_detected": self.contradictions_detected,
            "contradiction_rate": self.contradiction_rate,
            "records_superseded": self.records_superseded,
            "retrievals": self.retrievals,
        }
