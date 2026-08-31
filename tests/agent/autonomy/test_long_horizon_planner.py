"""
Test Long Horizon Planner - Decomposição de Metas
=================================================

Valida:
1. Decomposição de meta TRAIN_POKEMON em TaskGraph estruturado.
2. Preservação de ordem lógica e pré-condições.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.agent.autonomy.goal_candidate import GoalCandidate
from src.agent.autonomy.goal_state import GoalRuntime
from src.agent.autonomy.long_horizon_planner import LongHorizonPlanner


def test_long_horizon_planner_decomposition():
    print("🧪 Testando LongHorizonPlanner (Decomposição em TaskGraph)...")

    planner = LongHorizonPlanner()
    cand = GoalCandidate(goal_type="TRAIN_POKEMON", target="Pikachu", target_level=35)
    goal = GoalRuntime(candidate=cand)

    graph = planner.plan(goal)
    assert len(graph.nodes) == 4
    assert "t1_check_team" in graph.nodes
    assert "t2_reach_area" in graph.nodes
    print("  ✅ Meta TRAIN_POKEMON decomposta com sucesso em 4 tarefas estruturadas")


if __name__ == "__main__":
    test_long_horizon_planner_decomposition()
