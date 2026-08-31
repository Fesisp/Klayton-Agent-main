"""
Confidence Model - Modelo de Confiança por Origem de Evidência
===============================================================

Atribui níveis de confiança base por fonte de evidência e ajusta valores entre 0.0 e 1.0.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

from typing import Dict
from .provenance import EvidenceSource

BASE_CONFIDENCE_TABLE: Dict[EvidenceSource, float] = {
    EvidenceSource.USER_CONFIRMED: 0.98,
    EvidenceSource.DATABASE: 0.97,
    EvidenceSource.REPLAY_VALIDATED: 0.95,
    EvidenceSource.DIRECT_OBSERVATION: 0.90,
    EvidenceSource.OCR: 0.75,
    EvidenceSource.VLM: 0.70,
    EvidenceSource.INFERRED: 0.60,
    EvidenceSource.HEURISTIC: 0.50,
}


class ConfidenceModel:
    """Calculador de nível de confiança de memória."""

    @staticmethod
    def get_base_confidence(source: EvidenceSource) -> float:
        return BASE_CONFIDENCE_TABLE.get(source, 0.50)

    @staticmethod
    def clamp(value: float) -> float:
        return max(0.0, min(1.0, value))
