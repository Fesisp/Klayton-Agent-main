"""
Test Repetitive Behavior Guard - Detecção de Loops Repetitivos
=============================================================

Valida a interrupção ao detectar repetições de ações idênticas sem mudança de estado no mundo.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.compliance.repetitive_behavior_guard import RepetitiveBehaviorGuard


def test_repetitive_behavior_guard():
    print("🧪 Testando RepetitiveBehaviorGuard (Detecção de Loops)...")

    guard = RepetitiveBehaviorGuard(max_identical_actions=5, window_seconds=30.0)

    # 4 ações idênticas na mesma versão do mundo
    for _ in range(4):
        assert guard.record_action("MOVE", "NORTH", world_version=1) is False

    # 5ª ação sem avanço de versão -> Loop Detectado!
    assert guard.record_action("MOVE", "NORTH", world_version=1) is True
    print("  ✅ Loop repetitivo de ações sem avanço no mundo detectado e interrompido")


if __name__ == "__main__":
    test_repetitive_behavior_guard()
