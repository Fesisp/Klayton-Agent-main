"""
Autonomy Replay & Validation Harness
====================================

Validador de autonomia de metas e decomposição de longo alcance via replay determinístico sem abrir o jogo.
Calcula a taxa de conclusão de metas (Goal Completion Rate >= 90%).

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

from src.agent.autonomy.goal_candidate import GoalCandidate
from src.agent.autonomy.goal_state import GoalRuntime, GoalState
from src.agent.autonomy.goal_progress_evaluator import GoalProgressEvaluator
from src.agent.autonomy.autonomy_metrics import AutonomyMetrics
from src.world.world_state import WorldState, PokemonInfo


def run_autonomy_replay_validation(replay_path: Path) -> bool:
    print("====================================================")
    print("🎯 KLAYTON AUTONOMY REPLAY VALIDATION")
    print(f"📁 Replay File: {replay_path.name}")
    print("====================================================")

    if not replay_path.exists():
        print(f"❌ Erro: Arquivo de replay ausente em {replay_path}")
        return False

    with open(replay_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    evaluator = GoalProgressEvaluator()
    metrics = AutonomyMetrics()

    goal_dict = data.get("goal", {})
    cand = GoalCandidate(
        goal_type=goal_dict.get("type", "TRAIN_POKEMON"),
        target=goal_dict.get("target", "Pikachu"),
        target_level=goal_dict.get("target_level", 35)
    )
    goal_runtime = GoalRuntime(candidate=cand)
    goal_runtime.metadata["initial_level"] = goal_dict.get("initial_level", 30)

    metrics.goals_created += 1
    steps = data.get("steps", [])

    print(f"📊 Executando {len(steps)} passos da meta '{cand.goal_type}' ({cand.target} lvl {cand.target_level})...")

    world = WorldState()
    world.team.members.append(PokemonInfo(name=cand.target, level=30))

    for step in steps:
        s_id = step.get("step_id", 1)
        w_dict = step.get("world_state", {})
        world.team.members[0].level = w_dict.get("level", 30)

        prog = evaluator.evaluate(world, goal_runtime)
        metrics.tasks_completed += 1

        print(f"  Passo {s_id}: Tarefa={step.get('task')} -> Nível={world.team.members[0].level} -> Progresso={prog.fraction*100:.1f}% (Concluído={prog.complete})")

    if goal_runtime.progress >= 1.0 or prog.complete:
        metrics.goals_completed += 1
        goal_runtime.state = GoalState.COMPLETED

    rate = metrics.goal_completion_rate * 100
    print("\n----------------------------------------------------")
    print(f"📈 Taxa de Conclusão de Metas: {rate:.1f}% (Meta Mínima: 90.0%)")
    print("----------------------------------------------------")

    if rate >= 90.0:
        print("STATUS: AUTONOMY REPLAY VALIDATED (READY)")
        return True
    else:
        print("STATUS: AUTONOMY REPLAY FAILED")
        return False


def main():
    parser = argparse.ArgumentParser(description="Validador de Replay de Autonomia do Klayton")
    parser.add_argument("--replay", type=str, default=str(ROOT_DIR / "tests" / "fixtures" / "autonomy" / "train_to_level.json"), help="Caminho do arquivo de replay JSON")
    args = parser.parse_args()

    success = run_autonomy_replay_validation(Path(args.replay))
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
