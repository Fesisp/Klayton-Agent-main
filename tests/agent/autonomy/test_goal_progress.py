"""
Test Goal Progress Evaluator - Avaliação Empírica de Progresso
==============================================================

Valida:
1. Cálculo de fração de avanço (Nível 30 ➔ 33 / alvo 35 = 60%).
2. Conclusão da meta ao atingir o alvo (Nível 35 = 100% / COMPLETED).

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
from src.agent.autonomy.goal_progress_evaluator import GoalProgressEvaluator
from src.world.world_state import WorldState, PokemonInfo


def test_goal_progress_evaluator_levels():
    print("🧪 Testando GoalProgressEvaluator (Medição Empírica)...")

    evaluator = GoalProgressEvaluator()
    cand = GoalCandidate(goal_type="TRAIN_POKEMON", target="Pikachu", target_level=35)
    goal = GoalRuntime(candidate=cand)
    goal.metadata["initial_level"] = 30

    world = WorldState()
    world.team.members.append(PokemonInfo(name="Pikachu", level=33))

    # 1. Nível 33 -> 60%
    prog1 = evaluator.evaluate(world, goal)
    assert abs(prog1.fraction - 0.60) < 1e-4
    assert prog1.complete is False
    print("  ✅ Nível 33 calculou fração de avanço exata de 60.0%")

    # 2. Nível 35 -> Concluído
    world.team.members[0].level = 35
    prog2 = evaluator.evaluate(world, goal)
    assert prog2.fraction == 1.0
    assert prog2.complete is True
    print("  ✅ Nível 35 confirmou conclusão completa da meta (100.0%)")


if __name__ == "__main__":
    test_goal_progress_evaluator_levels()
