"""
Runtime Scheduler - Agendador de Ticks por Classe de Prioridade
================================================================

Gerencia a frequência de execução dos subsistemas sem busy waits (REALTIME, FAST, NORMAL, BACKGROUND).

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

import time
from enum import Enum
from typing import Dict, Optional


class TickClass(Enum):
    REALTIME = "realtime"      # ~30 Hz (0.033s)
    FAST = "fast"              # ~10 Hz (0.10s)
    NORMAL = "normal"          # ~2 Hz (0.50s)
    BACKGROUND = "background"  # ~0.1 Hz (10.0s)


class RuntimeScheduler:
    """Agendador de ticks por classe de frequência."""

    INTERVALS: Dict[TickClass, float] = {
        TickClass.REALTIME: 0.033,
        TickClass.FAST: 0.10,
        TickClass.NORMAL: 0.50,
        TickClass.BACKGROUND: 10.0,
    }

    def __init__(self):
        self.last_ticks: Dict[TickClass, float] = {}

    def should_tick(self, tick_class: TickClass, now: Optional[float] = None) -> bool:
        now = now or time.time()
        last = self.last_ticks.get(tick_class, 0.0)
        interval = self.INTERVALS.get(tick_class, 0.50)

        if now - last >= interval:
            self.last_ticks[tick_class] = now
            return True
        return False
