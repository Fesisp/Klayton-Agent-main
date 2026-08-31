"""
Session Guard - Guarda de Duração de Sessão Contínua
====================================================

Monitora a duração da sessão contínua para evitar execução prolongada não supervisionada.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

import time
from typing import Optional


class SessionGuard:
    """Guarda de limite de duração de sessão."""

    def __init__(self, max_minutes: int = 60):
        self.max_seconds = max_minutes * 60.0
        self.started_at = time.monotonic()
        self.paused_duration = 0.0

    def exceeded(self, now: Optional[float] = None) -> bool:
        """Retorna True se a sessão contínua ultrapassou o limite máximo."""
        now = now or time.monotonic()
        elapsed = now - self.started_at - self.paused_duration
        return elapsed >= self.max_seconds

    def reset(self) -> None:
        self.started_at = time.monotonic()
        self.paused_duration = 0.0
