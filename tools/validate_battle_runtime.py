"""
Battle Runtime Replay & Validation Harness
===========================================

Ferramenta de validação via replay determinístico sem necessidade de abrir o jogo.
Reproduz a sequência de observações registradas e avalia a taxa de confirmação de ações (>= 90%).

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

import sys
import json
import argparse
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.battle.runtime.battle_observation import BattleObservation
from src.battle.runtime.battle_state_tracker import BattleStateTracker
from src.battle.runtime.battle_action import BattleAction, BattleActionType
from src.battle.runtime.battle_outcome_verifier import BattleOutcomeVerifier, OutcomeStatus
from src.battle.runtime.battle_metrics import BattleMetrics


def run_replay_validation(replay_path: Path) -> bool:
    print("====================================================")
    print("⚔️ KLAYTON BATTLE RUNTIME REPLAY VALIDATION")
    print(f"📁 Replay File: {replay_path.name}")
    print("====================================================")

    if not replay_path.exists():
        print(f"❌ Erro: Arquivo de replay ausente em {replay_path}")
        return False

    with open(replay_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    tracker = BattleStateTracker()
    verifier = BattleOutcomeVerifier()
    metrics = BattleMetrics()

    turns = data.get("turns", [])
    print(f"📊 Processando {len(turns)} turnos gravados na sessão '{data.get('session_id')}'...")

    for turn in turns:
        t_id = turn.get("turn_id", 1)
        obs_b_dict = turn.get("observation_before", {})
        obs_a_dict = turn.get("observation_after", {})

        obs_b = BattleObservation(**obs_b_dict)
        obs_a = BattleObservation(**obs_a_dict)

        # Atualiza o tracker com observações
        events_b = tracker.update(obs_b)
        events_a = tracker.update(obs_a)

        # Monta a ação
        act_dict = turn.get("decision", {}).get("action", {})
        action_type_str = act_dict.get("type", "move")
        action = BattleAction(
            type=BattleActionType(action_type_str),
            move_slot=act_dict.get("move_slot"),
            reason=act_dict.get("reason")
        )

        outcome = verifier.verify(action, obs_b, [obs_a], events_a or events_b)
        metrics.record_action(outcome.status.value)

        print(f"  Turno {t_id}: Ação={action.type.value} -> Status={outcome.status.value.upper()} (Confiança={outcome.confidence:.2f})")

    rate = metrics.action_confirmation_rate * 100
    print("\n----------------------------------------------------")
    print(f"📈 Taxa de Confirmação de Ações: {rate:.1f}% (Meta Mínima: 90.0%)")
    print("----------------------------------------------------")

    if rate >= 90.0:
        print("STATUS: REPLAY VALIDATED (READY)")
        return True
    else:
        print("STATUS: REPLAY FAILED")
        return False


def main():
    parser = argparse.ArgumentParser(description="Validador de Replay de Batalha do Klayton")
    parser.add_argument("--replay", type=str, default=str(ROOT_DIR / "tests" / "fixtures" / "battles" / "simple_win.json"), help="Caminho do arquivo de replay JSON")
    args = parser.parse_args()

    success = run_replay_validation(Path(args.replay))
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
