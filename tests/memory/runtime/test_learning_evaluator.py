"""
Test Learning Evaluator - Extração de Aprendizados
===================================================

Valida geração de registros de memória episódica a partir de dados brutos de resultado de batalha e navegação.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.memory.runtime.learning_evaluator import LearningEvaluator


def test_learning_evaluator_outcomes():
    print("🧪 Testando LearningEvaluator (Extração de Aprendizado)...")

    evaluator = LearningEvaluator()

    rec_b = evaluator.evaluate_battle_outcome({"enemy_name": "Pikachu", "action": "tackle", "success": True})
    assert rec_b.key == "battle_strategy_Pikachu"
    assert rec_b.confidence == 0.90
    print("  ✅ Resultado de batalha avaliado e convertido em MemoryRecord episódico")

    rec_n = evaluator.evaluate_navigation_outcome({"source": "Pallet", "target": "Viridian", "success": True, "duration": 5.2})
    assert rec_n.key == "route_reliability_Pallet_to_Viridian"
    assert rec_n.confidence == 0.95
    print("  ✅ Resultado de navegação avaliado e convertido em MemoryRecord episódico")


if __name__ == "__main__":
    test_learning_evaluator_outcomes()
