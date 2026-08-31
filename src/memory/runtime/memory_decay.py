"""
Memory Decay - Decaimento Temporal de Confiança Contextual
===========================================================

Aplica decaimento temporal à confiança de conhecimentos contextuais mantendo dados canônicos intactos.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

import math
import time
from .memory_record import MemoryRecord
from .provenance import EvidenceSource


class MemoryDecay:
    """Calculador de decaimento temporal de confiança."""

    @staticmethod
    def apply_decay(record: MemoryRecord, decay_rate: float = 0.001, now: float = None) -> float:
        now = now or time.time()
        # Conhecimento canônico ou confirmado pelo usuário não sofre decaimento
        if record.source in [EvidenceSource.USER_CONFIRMED, EvidenceSource.DATABASE]:
            return record.confidence

        age = max(0.0, now - record.updated_at)
        decayed = record.confidence * math.exp(-decay_rate * (age / 3600.0))
        return max(0.10, min(1.0, decayed))
