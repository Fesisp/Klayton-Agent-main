"""
Action Rate Limiter - Limitador de Taxa de Acionamentos
======================================================

Garante que o envio de inputs físicos não ultrapasse o limite de frequência configurado (ex: 8 acionamentos/s).

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

import time
from collections import deque


class ActionRateLimiter:
    """Limitador determinístico de frequência de acionamentos."""

    def __init__(self, max_actions_per_second: float = 8.0):
        self.max_actions_per_second = max_actions_per_second
        self.timestamps: deque[float] = deque()

    def allow(self) -> bool:
        """Retorna True se o acionamento estiver dentro do limite de taxa."""
        now = time.monotonic()

        while self.timestamps and now - self.timestamps[0] > 1.0:
            self.timestamps.popleft()

        if len(self.timestamps) >= self.max_actions_per_second:
            return False

        self.timestamps.append(now)
        return True
