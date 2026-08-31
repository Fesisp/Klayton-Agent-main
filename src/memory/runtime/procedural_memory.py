"""
Procedural Memory - Desempenho de Estratégias e Procedimentos
=============================================================

Mede a taxa de sucesso empírica de rotas, estratégias e táticas com suavização de Laplace.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Dict, Optional
from .memory_store import MemoryStore


@dataclass
class ProcedureStats:
    """Estatísticas de desempenho procedural."""
    key: str

    attempts: int = 0
    successes: int = 0
    failures: int = 0

    average_cost: float = 0.0
    average_duration: float = 0.0

    last_used: Optional[float] = None

    @property
    def success_rate(self) -> float:
        """Suavização de Laplace: (successes + 1) / (attempts + 2)."""
        return (self.successes + 1.0) / (self.attempts + 2.0)


class ProceduralMemory:
    """Gerenciador de estatísticas procedurais."""

    def __init__(self, store: MemoryStore):
        self.store = store
        self.cache: Dict[str, ProcedureStats] = {}

    def record_attempt(self, key: str, success: bool, duration: float = 0.0, cost: float = 1.0) -> ProcedureStats:
        stats = self.get_stats(key)
        stats.attempts += 1
        if success:
            stats.successes += 1
        else:
            stats.failures += 1

        stats.average_cost = (stats.average_cost * (stats.attempts - 1) + cost) / stats.attempts
        stats.average_duration = (stats.average_duration * (stats.attempts - 1) + duration) / stats.attempts
        stats.last_used = time.time()

        self.cache[key] = stats
        return stats

    def get_stats(self, key: str) -> ProcedureStats:
        if key in self.cache:
            return self.cache[key]
        stats = ProcedureStats(key=key)
        self.cache[key] = stats
        return stats
