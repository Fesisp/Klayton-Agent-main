"""
Test Compliance Integration - Integração de Compliance e InputGuard
====================================================================

Valida a integração completa entre a camada de compliance e o InputGuard.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.input.input_guard import InputGuard


def test_compliance_input_guard_integration():
    print("🧪 Testando Integração entre Compliance e InputGuard...")

    guard = InputGuard(max_actions_per_second=8.0)

    for _ in range(8):
        assert guard.allow_action() is True

    # 9ª ação deve ser bloqueada via Compliance Rate Limiter
    assert guard.allow_action() is False
    print("  ✅ Trava de taxa de compliance (8 acionamentos/s) aplicada com sucesso pelo InputGuard")


if __name__ == "__main__":
    test_compliance_input_guard_integration()
