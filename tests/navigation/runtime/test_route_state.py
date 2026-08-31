"""
Test Route State - Estado e Avanço de Rota
===========================================

Valida:
1. Inspeção do nó atual da rota.
2. Avanço controlado de waypoint sem antecipar conclusões.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.navigation.runtime.route_state import RouteState


def test_route_state_advancement():
    print("🧪 Testando RouteState (Avanço de Waypoint)...")

    route = RouteState(route_id="r1", nodes=["Pallet Town", "Route 1", "Viridian City"])

    assert route.current_node() == "Pallet Town"
    assert route.completed is False

    res1 = route.advance()
    assert res1 is True
    assert route.current_node() == "Route 1"
    print("  ✅ Avançou do nó 0 (Pallet Town) para o nó 1 (Route 1)")

    res2 = route.advance()
    assert res2 is True
    assert route.completed is True
    print("  ✅ Concluiu a rota ao atingir o nó final (Viridian City)")


if __name__ == "__main__":
    test_route_state_advancement()
