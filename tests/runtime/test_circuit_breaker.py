"""
Test Circuit Breaker - Transições de Estado de Disjuntor
=========================================================

Valida transições (CLOSED ➔ OPEN ➔ HALF_OPEN ➔ CLOSED) e bloqueio de requisições durante falhas.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

import sys
import time
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.runtime.circuit_breaker import CircuitBreaker, CircuitState


def test_circuit_breaker_transitions():
    print("🧪 Testando CircuitBreaker (Isolamento de Falhas Externas)...")

    cb = CircuitBreaker(failure_threshold=2, recovery_timeout_seconds=0.1)

    assert cb.allow_request() is True

    cb.record_failure()
    assert cb.state == CircuitState.CLOSED

    cb.record_failure()
    assert cb.state == CircuitState.OPEN
    assert cb.allow_request() is False
    print("  ✅ Disjuntor abriu (OPEN) após 2 falhas consecutivas e bloqueou novas chamadas")

    time.sleep(0.15)
    assert cb.allow_request() is True
    assert cb.state == CircuitState.HALF_OPEN
    print("  ✅ Disjuntor transicionou para HALF_OPEN após timeout de recuperação")


if __name__ == "__main__":
    test_circuit_breaker_transitions()
