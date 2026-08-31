"""
Watchdog - Monitoramento de Heartbeats e Latência de Ticks
=========================================================

Monitora a atualização de heartbeats dos subsistemas para detectar travamentos ou deadlocks.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

import time
from typing import Dict, Optional
from .subsystem_state import SubsystemState


class Watchdog:
    """Watchdog de verificação de travamento de subsistemas."""

    def __init__(self, timeout_seconds: float = 5.0):
        self.timeout_seconds = timeout_seconds
        self.heartbeats: Dict[str, float] = {}

    def heartbeat(self, subsystem_name: str) -> None:
        self.heartbeats[subsystem_name] = time.time()

    def check_subsystem(self, subsystem_name: str, now: Optional[float] = None) -> bool:
        """Retorna True se o subsistema estiver saudável (heartbeat recente)."""
        now = now or time.time()
        last = self.heartbeats.get(subsystem_name)
        if last is None:
            return True
        return (now - last) <= self.timeout_seconds
