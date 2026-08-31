"""
Test Supervision Gate - Avaliação de Foco, Confiança e Saúde
============================================================

Valida as decisões do SupervisionGate (ALLOW, PAUSE, BLOCK) com base na percepção e foco de janela.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.compliance.supervision_gate import SupervisionGate, SupervisionDecision


def test_supervision_gate_evaluations():
    print("🧪 Testando SupervisionGate (Avaliação de Segurança)...")

    gate = SupervisionGate()

    assert gate.evaluate(world_confidence=0.90, window_focused=True, runtime_healthy=True) == SupervisionDecision.ALLOW
    assert gate.evaluate(world_confidence=0.50, window_focused=True, runtime_healthy=True) == SupervisionDecision.PAUSE
    assert gate.evaluate(world_confidence=0.90, window_focused=False, runtime_healthy=True) == SupervisionDecision.BLOCK
    print("  ✅ Decisões ALLOW, PAUSE (confiança < 0.70) e BLOCK (sem foco) validadas com sucesso")


if __name__ == "__main__":
    test_supervision_gate_evaluations()
