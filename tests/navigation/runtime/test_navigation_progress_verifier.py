"""
Test Navigation Progress Verifier - Validação Empírica de Avanço
================================================================

Valida:
1. Pressionamento de tecla sem deslocamento físico (NO_PROGRESS).
2. Deslocamento >= 0.5 unidades (PROGRESS).
3. Alteração de mapa (MAP_CHANGED).
4. Chegada ao destino (ARRIVED).

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.navigation.runtime.navigation_action import NavigationAction, NavigationActionType
from src.navigation.runtime.navigation_progress import NavigationProgress
from src.navigation.runtime.navigation_progress_verifier import NavigationProgressVerifier
from src.world.model.world_location import WorldLocation, LocationConfidence


def test_navigation_progress_verifier_scenarios():
    print("🧪 Testando NavigationProgressVerifier (Ciclo Fechado de Avanço Espacial)...")

    verifier = NavigationProgressVerifier(minimum_progress_distance=0.5)

    loc1 = WorldLocation(map_id="Pallet Town", x=0.0, y=0.0, confidence=LocationConfidence.HIGH)
    act = NavigationAction(type=NavigationActionType.MOVE, direction="w")

    # 1. Pressionamento de tecla sem deslocamento -> NO_PROGRESS
    p1 = verifier.verify(loc1, act, loc1)
    assert p1 == NavigationProgress.NO_PROGRESS
    print("  ✅ Teste 1: Movimento sem alteração de coordenadas retornou NO_PROGRESS (Tecla != Progresso)")

    # 2. Deslocamento físico >= 0.5 -> PROGRESS
    loc2 = WorldLocation(map_id="Pallet Town", x=1.0, y=0.0, confidence=LocationConfidence.HIGH)
    p2 = verifier.verify(loc1, act, loc2)
    assert p2 == NavigationProgress.PROGRESS
    print("  ✅ Teste 2: Deslocamento de 1.0 unidade retornou PROGRESS")

    # 3. Alteração de mapa -> MAP_CHANGED
    loc_map2 = WorldLocation(map_id="Route 1", x=0.0, y=10.0, confidence=LocationConfidence.HIGH)
    p3 = verifier.verify(loc1, act, loc_map2)
    assert p3 == NavigationProgress.MAP_CHANGED
    print("  ✅ Teste 3: Alteração de map_id retornou MAP_CHANGED")

    # 4. Chegada ao destino -> ARRIVED
    dest = WorldLocation(map_id="Route 1", x=0.0, y=10.5, confidence=LocationConfidence.HIGH)
    p4 = verifier.verify(loc_map2, act, dest, destination=dest)
    assert p4 == NavigationProgress.ARRIVED
    print("  ✅ Teste 4: Proximidade do destino final retornou ARRIVED com sucesso")


if __name__ == "__main__":
    test_navigation_progress_verifier_scenarios()
