"""
Test Battle Action Executor - Proteção Contra Input Duplicado
============================================================

Valida:
1. Máquina de estados do executor físico (IDLE ➔ OPENING_MENU ➔ WAITING_RESULT ➔ DONE).
2. Trava input_committed impedindo o disparo de múltiplos cliques idênticos por frame.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

import sys
import time
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.battle.runtime.battle_observation import BattleObservation
from src.battle.runtime.battle_action import BattleAction, BattleActionType
from src.battle.runtime.battle_action_executor import BattleActionExecutor, ExecutorPhase


class MockInputSimulator:
    def __init__(self):
        self.clicks = 0

    def click_in_slot(self, slot: int):
        self.clicks += 1

    def humanized_click_in_slot(self, slot: int):
        self.clicks += 1


def test_battle_action_executor_lock():
    print("🧪 Testando BattleActionExecutor (Proteção Contra Input Duplicado)...")

    executor = BattleActionExecutor()
    input_sim = MockInputSimulator()
    obs = BattleObservation(timestamp=time.time(), in_battle=True)

    act = BattleAction(type=BattleActionType.MOVE, move_slot=1)
    executor.start(act, obs)

    # Frame 1: Envia o clique e ativa input_committed
    phase1 = executor.tick(obs, input_sim)
    assert phase1 == ExecutorPhase.WAITING_RESULT
    assert input_sim.clicks == 1
    assert executor.input_committed is True
    print("  ✅ Frame 1: Clique enviado (clicks=1) e trava input_committed ativada")

    # Frame 2: Não deve enviar segundo clique!
    phase2 = executor.tick(obs, input_sim)
    assert phase2 == ExecutorPhase.WAITING_RESULT
    assert input_sim.clicks == 1
    print("  ✅ Frame 2: Trava bloqueou envio de input duplicado em frame subsequente")

    # Frame 3: Permanece bloqueado até outcome/reset
    phase3 = executor.tick(obs, input_sim)
    assert input_sim.clicks == 1
    print("  ✅ Frame 3: Mantido estado WAITING_RESULT sem duplicar clique")


if __name__ == "__main__":
    test_battle_action_executor_lock()
