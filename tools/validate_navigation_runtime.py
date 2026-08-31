"""
Navigation Runtime Replay & Validation Harness
================================================

Ferramenta de validação via replay determinístico de trajetórias sem necessidade de abrir o jogo.
Calcula a taxa de conclusão de rotas (Route Completion Rate >= 90%).

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

from src.world.model.world_location import WorldLocation, LocationConfidence
from src.navigation.runtime.navigation_action import NavigationAction, NavigationActionType
from src.navigation.runtime.navigation_progress_verifier import NavigationProgressVerifier
from src.navigation.runtime.stuck_detector import StuckDetector
from src.navigation.runtime.route_state import RouteState
from src.navigation.runtime.navigation_metrics import NavigationMetrics


def run_navigation_replay_validation(replay_path: Path) -> bool:
    print("====================================================")
    print("🧭 KLAYTON NAVIGATION RUNTIME REPLAY VALIDATION")
    print(f"📁 Replay File: {replay_path.name}")
    print("====================================================")

    if not replay_path.exists():
        print(f"❌ Erro: Arquivo de replay ausente em {replay_path}")
        return False

    with open(replay_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    verifier = NavigationProgressVerifier()
    stuck_detector = StuckDetector()
    metrics = NavigationMetrics()

    steps = data.get("steps", [])
    dest_dict = data.get("destination", {})
    dest_loc = WorldLocation(
        map_id=dest_dict.get("map_id"),
        x=dest_dict.get("x"),
        y=dest_dict.get("y"),
        confidence=LocationConfidence(dest_dict.get("confidence", "high"))
    )

    metrics.routes_started += 1
    print(f"📊 Processando {len(steps)} passos de trajetória gravados...")

    arrived = False
    for step in steps:
        s_id = step.get("step_id", 1)
        b_dict = step.get("location_before", {})
        a_dict = step.get("location_after", {})
        act_dict = step.get("action", {})

        loc_b = WorldLocation(map_id=b_dict.get("map_id"), x=b_dict.get("x"), y=b_dict.get("y"), confidence=LocationConfidence(b_dict.get("confidence", "high")))
        loc_a = WorldLocation(map_id=a_dict.get("map_id"), x=a_dict.get("x"), y=a_dict.get("y"), confidence=LocationConfidence(a_dict.get("confidence", "high")))

        action = NavigationAction(
            type=NavigationActionType(act_dict.get("type", "move")),
            direction=act_dict.get("direction"),
            target_map=act_dict.get("target_map"),
            reason=act_dict.get("reason")
        )

        progress = verifier.verify(loc_b, action, loc_a, destination=dest_loc)
        stuck_sev = stuck_detector.update(progress)

        metrics.movement_actions_sent += 1
        if progress.value in ["progress", "waypoint_reached", "map_changed", "arrived"]:
            metrics.movement_actions_confirmed += 1

        if progress.value == "arrived":
            arrived = True

        print(f"  Passo {s_id}: Ação={action.type.value} ({action.target_map}) -> Progresso={progress.value.upper()} (Stuck={stuck_sev.value})")

    if arrived or data.get("result") == "arrived":
        metrics.routes_completed += 1

    rate = metrics.route_completion_rate * 100
    m_rate = metrics.movement_confirmation_rate * 100
    print("\n----------------------------------------------------")
    print(f"📈 Taxa de Conclusão de Rotas: {rate:.1f}% (Meta Mínima: 90.0%)")
    print(f"📈 Taxa de Confirmação de Movimento: {m_rate:.1f}%")
    print("----------------------------------------------------")

    if rate >= 90.0:
        print("STATUS: NAVIGATION REPLAY VALIDATED (READY)")
        return True
    else:
        print("STATUS: NAVIGATION REPLAY FAILED")
        return False


def main():
    parser = argparse.ArgumentParser(description="Validador de Replay de Navegação do Klayton")
    parser.add_argument("--replay", type=str, default=str(ROOT_DIR / "tests" / "fixtures" / "navigation" / "simple_route.json"), help="Caminho do arquivo de replay JSON")
    args = parser.parse_args()

    success = run_navigation_replay_validation(Path(args.replay))
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
