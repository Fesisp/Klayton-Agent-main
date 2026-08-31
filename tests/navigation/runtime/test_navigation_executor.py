"""
Test Navigation Executor - Executor Físico de Comandos de Movimento
===================================================================

Valida:
1. Tradução de NavigationAction em acionamento do InputSimulator.
2. Transições de fase (IDLE ➔ INPUT_SENT ➔ WAITING_OBSERVATION ➔ DONE).

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.navigation.runtime.navigation_action import NavigationAction, NavigationActionType
from src.navigation.runtime.navigation_executor import NavigationExecutor, NavigationExecutorPhase


class MockInputSimulator:
    def __init__(self):
        self.pressed_keys = []

    def press(self, key: str):
        self.pressed_keys.append(key)


def test_navigation_executor_phase():
    print("🧪 Testando NavigationExecutor (Fases da Execução Física)...")

    executor = NavigationExecutor()
    input_sim = MockInputSimulator()

    act = NavigationAction(type=NavigationActionType.MOVE, direction="w")
    executor.start(act)
    assert executor.phase == NavigationExecutorPhase.INPUT_SENT

    phase1 = executor.tick(input_sim)
    assert phase1 == NavigationExecutorPhase.WAITING_OBSERVATION
    assert input_sim.pressed_keys == ["w"]
    print("  ✅ Tecla 'w' enviada ao InputSimulator e fase alterada para WAITING_OBSERVATION")


if __name__ == "__main__":
    test_navigation_executor_phase()
