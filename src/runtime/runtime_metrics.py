"""
Runtime Metrics - Métricas de Latência e Prontidão de Runtime
============================================================

Mede latências de ticks (p50, p95, p99) e monitora a prontidão global do agente.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Any


@dataclass
class RuntimeMetrics:
    """Métricas de desempenho e saúde de runtime."""
    uptime_seconds: float = 0.0
    tick_latencies_ms: List[float] = field(default_factory=list)

    total_faults: int = 0
    recoveries_total: int = 0
    fatal_faults: int = 0

    @property
    def p95_latency_ms(self) -> float:
        if not self.tick_latencies_ms:
            return 0.0
        sorted_lat = sorted(self.tick_latencies_ms)
        idx = int(len(sorted_lat) * 0.95)
        return sorted_lat[min(idx, len(sorted_lat) - 1)]

    def record_tick_latency(self, latency_ms: float) -> None:
        self.tick_latencies_ms.append(latency_ms)
        if len(self.tick_latencies_ms) > 1000:
            self.tick_latencies_ms.pop(0)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "uptime_seconds": self.uptime_seconds,
            "p95_latency_ms": self.p95_latency_ms,
            "total_faults": self.total_faults,
            "recoveries_total": self.recoveries_total,
            "fatal_faults": self.fatal_faults,
        }
