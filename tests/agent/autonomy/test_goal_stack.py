"""
Test Goal Stack - Pilha de Objetivos e Gerenciamento de Interrupção
===================================================================

Valida:
1. Empilhamento e suspensão da meta anterior.
2. Desempilhamento de meta concluída e retomada de meta suspenso.

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
from src.agent.autonomy.goal_state import GoalRuntime, GoalState
from src.agent.autonomy.goal_stack import GoalStack


def test_goal_stack_push_pop_resume():
    print("🧪 Testando GoalStack (Suspensão e Retomada)...")

    stack = GoalStack()

    g1 = GoalRuntime(candidate=GoalCandidate(goal_type="TRAIN_POKEMON"))
    stack.push(g1)
    assert stack.active().candidate.goal_type == "TRAIN_POKEMON"
    assert g1.state == GoalState.ACTIVE
    print("  ✅ Meta 1 (TRAIN_POKEMON) empilhada e marcada como ACTIVE")

    g2 = GoalRuntime(candidate=GoalCandidate(goal_type="HEAL_TEAM"))
    stack.push(g2)
    assert stack.active().candidate.goal_type == "HEAL_TEAM"
    assert g1.state == GoalState.SUSPENDED
    assert g2.state == GoalState.ACTIVE
    print("  ✅ Meta 2 (HEAL_TEAM) empilhada, suspendendo Meta 1")

    # Conclui a meta de cura
    g2.state = GoalState.COMPLETED
    resumed = stack.resume_previous()
    assert resumed.candidate.goal_type == "TRAIN_POKEMON"
    assert g1.state == GoalState.ACTIVE
    print("  ✅ Meta 2 concluída e Meta 1 (TRAIN_POKEMON) retomada com sucesso")


if __name__ == "__main__":
    test_goal_stack_push_pop_resume()
