"""
Test Explanation Engine - Motor de Explicação de Decisões
==========================================================

Valida a geração de explicações fundamentadas estritamente em evidências observáveis do WorldState.

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
from src.world.world_state import WorldState, PokemonInfo
from src.interaction.runtime.explanation_engine import ExplanationEngine


def test_explanation_engine_real_state():
    print("🧪 Testando ExplanationEngine (Explicações Transparentes)...")

    engine = ExplanationEngine()
    world = WorldState()
    world.team.members.append(PokemonInfo(name="Pikachu", level=33, hp_percentage=0.15))

    cand = GoalCandidate(goal_type="TRAIN_POKEMON", target="Pikachu", target_level=35)
    goal = GoalRuntime(candidate=cand)

    explanation = engine.explain(world, goal)
    assert "curar o time" in explanation.summary
    assert "needs_healing == True" in explanation.evidence[0]
    print("  ✅ Explicação gerada citou a evidência real (world.team.needs_healing == True) sem inventar estado")


if __name__ == "__main__":
    test_explanation_engine_real_state()
