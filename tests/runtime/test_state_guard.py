"""
Test State Guard - Invariantes Globais e Decisões Obsoletas
===========================================================

Valida a checagem de invariantes de estado e rejeição de decisões baseadas em versões antigas do WorldState.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.runtime.state_guard import StateGuard
from src.world.world_state import WorldState


def test_state_guard_versioning():
    print("🧪 Testando StateGuard (Versionamento e Invariantes)...")

    sg = StateGuard()
    world = WorldState()

    world.update_player(map_name="Route 1")
    v1 = world.version
    assert v1 > 0

    assert sg.is_decision_stale(decision_world_version=v1, current_world_version=v1 + 2) is False
    assert sg.is_decision_stale(decision_world_version=v1, current_world_version=v1 + 20) is True
    print("  ✅ Decisão antiga (diferença de 20 versões) identificada como obsoleta (Stale Decision)")


if __name__ == "__main__":
    test_state_guard_versioning()
