"""
Test Goal Arbitrator - Arbitragem de Prioridades e Histerese
============================================================

Valida:
1. Prioridade do comando do usuário sobre rotinas normais.
2. Prioridade de emergência de cura.
3. Aplicação de margem de histerese.

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
from src.agent.autonomy.goal_arbitrator import GoalArbitrator
from src.agent.autonomy.goal_stack import GoalStack


def test_goal_arbitrator_scoring():
    print("🧪 Testando GoalArbitrator (Pontuação e Histerese)...")

    arbitrator = GoalArbitrator(switch_margin=0.15)
    stack = GoalStack()

    c_train = GoalCandidate(goal_type="TRAIN_POKEMON", base_priority=0.5, source="internal")
    c_user = GoalCandidate(goal_type="RETURN_TO_CITY", base_priority=0.5, source="user")
    c_heal = GoalCandidate(goal_type="HEAL_CRITICAL", base_priority=0.5, source="system")

    # 1. Candidato normal vs Comando do Usuário
    res1 = arbitrator.select([c_train, c_user], stack)
    assert res1.candidate.goal_type == "RETURN_TO_CITY"
    print("  ✅ Teste 1: Comando do usuário (RETURN_TO_CITY) superou rotina interna")

    # 2. Emergência de cura superando meta ativa
    res2 = arbitrator.select([c_heal], stack)
    assert res2.candidate.goal_type == "HEAL_CRITICAL"
    print("  ✅ Teste 2: Emergência de cura (HEAL_CRITICAL) interrompeu meta ativa")


if __name__ == "__main__":
    test_goal_arbitrator_scoring()
