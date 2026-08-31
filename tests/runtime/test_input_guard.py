"""
Test Input Guard - Limite de Taxa e Parada de Emergência
=========================================================

Valida a imposição do limite de taxa de ações (15 acionamentos/s) e disparo da Parada de Emergência.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.input.input_guard import InputGuard


class MockInputSimulator:
    def __init__(self):
        self.released = False

    def release_all(self):
        self.released = True


def test_input_guard_protections():
    print("🧪 Testando InputGuard (Limite de Taxa e Emergência)...")

    guard = InputGuard(max_actions_per_second=3)
    sim = MockInputSimulator()

    assert guard.allow_action() is True
    assert guard.allow_action() is True
    assert guard.allow_action() is True
    assert guard.allow_action() is False
    print("  ✅ Limite de taxa de 3 acionamentos/s bloqueou a 4ª tentativa")

    guard.trigger_emergency_stop(sim)
    assert guard.emergency_stop_active is True
    assert sim.released is True
    assert guard.allow_action() is False
    print("  ✅ Parada de Emergência acionada, teclas liberadas e novas ações bloqueadas")


if __name__ == "__main__":
    test_input_guard_protections()
