"""
Test Interaction Policy - Limites de Execução por Confiança
============================================================

Valida regras de permissão de execução de comandos com base em limites de confiança.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.interaction.runtime.interaction_policy import InteractionPolicy


def test_interaction_policy_thresholds():
    print("🧪 Testando InteractionPolicy (Limites de Confiança)...")

    policy = InteractionPolicy(command_min_confidence=0.75, critical_command_min_confidence=0.90)

    assert policy.allow_execution(0.80, is_critical=False) is True
    assert policy.allow_execution(0.80, is_critical=True) is False
    assert policy.allow_execution(0.95, is_critical=True) is True
    print("  ✅ Limites de confiança para comandos normais (0.75) e críticos (0.90) respeitados")


if __name__ == "__main__":
    test_interaction_policy_thresholds()
