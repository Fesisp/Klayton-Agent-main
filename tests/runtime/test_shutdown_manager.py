"""
Test Shutdown Manager - Idempotência e Desligamento Seguro
==========================================================

Valida a liberação de inputs e idempotência do ShutdownManager (múltiplas chamadas não geram erros).

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.runtime.shutdown_manager import ShutdownManager


class MockInputSimulator:
    def __init__(self):
        self.released = False

    def release_all(self):
        self.released = True


def test_shutdown_manager_idempotency():
    print("🧪 Testando ShutdownManager (Idempotência e Liberação)...")

    sm = ShutdownManager()
    sim = MockInputSimulator()

    assert sm.shutdown(sim) is True
    assert sim.released is True

    # Segunda chamada (idempotente)
    assert sm.shutdown(sim) is True
    print("  ✅ Shutdown executado e verificado como idempotente")


if __name__ == "__main__":
    test_shutdown_manager_idempotency()
