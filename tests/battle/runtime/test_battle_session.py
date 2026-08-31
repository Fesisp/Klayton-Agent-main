"""
Test Battle Session, Recorder & Metrics
=======================================

Valida a gravação de sessão em JSON e o cálculo da taxa de confirmação (Action Confirmation Rate).

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

from src.battle.runtime.battle_session import BattleSession
from src.battle.runtime.battle_recorder import BattleRecorder
from src.battle.runtime.battle_metrics import BattleMetrics


def test_battle_session_recording():
    print("🧪 Testando BattleSession, Recorder & BattleMetrics...")

    session = BattleSession(id="test_session_999", enemy_name="Charizard", result="won")
    session.decisions.append({"turn": 1, "action": "MOVE", "slot": 0})
    session.actions.append({"turn": 1, "status": "confirmed"})

    recorder = BattleRecorder(output_dir=Path("scratch/test_battles"))
    json_path = recorder.save_session(session)

    assert json_path.exists()
    print(f"  ✅ Sessão gravada com sucesso em JSON: {json_path.name}")

    metrics = BattleMetrics()
    metrics.record_action("confirmed")
    metrics.record_action("confirmed")
    metrics.record_action("confirmed")
    metrics.record_action("rejected")

    assert metrics.actions_total == 4
    assert metrics.actions_confirmed == 3
    assert abs(metrics.action_confirmation_rate - 0.75) < 1e-4
    print(f"  ✅ Métricas calculadas: Total={metrics.actions_total} | Confirmation Rate={metrics.action_confirmation_rate*100:.1f}%")


if __name__ == "__main__":
    test_battle_session_recording()
