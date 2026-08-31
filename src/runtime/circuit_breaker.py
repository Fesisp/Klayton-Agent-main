"""
Circuit Breaker - Disjuntor de Proteção Contra Serviços Externos
================================================================

Protege a execução do agente isolando falhas repetidas em serviços externos (VLM, TTS, APIs).

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

import time
from enum import Enum


class CircuitState(Enum):
    CLOSED = "closed"        # Serviço operacional
    OPEN = "open"            # Disjuntor aberto devido a falhas recorrentes
    HALF_OPEN = "half_open"  # Testando recuperação


class CircuitBreaker:
    """Disjuntor para isolamento de falhas externas."""

    def __init__(self, failure_threshold: int = 3, recovery_timeout_seconds: float = 30.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout_seconds = recovery_timeout_seconds

        self.state: CircuitState = CircuitState.CLOSED
        self.failure_count: int = 0
        self.last_state_change: float = time.time()

    def record_success(self) -> None:
        self.failure_count = 0
        self.state = CircuitState.CLOSED

    def record_failure(self) -> None:
        self.failure_count += 1
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            self.last_state_change = time.time()

    def allow_request(self) -> bool:
        if self.state == CircuitState.CLOSED:
            return True
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_state_change >= self.recovery_timeout_seconds:
                self.state = CircuitState.HALF_OPEN
                return True
            return False
        if self.state == CircuitState.HALF_OPEN:
            return True
        return False
