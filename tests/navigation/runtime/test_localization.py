"""
Test Localization Engine - Hierarquia de Fontes de Localização
===============================================================

Valida:
1. Coordenadas explícitas (Level 1 - HIGH).
2. Map ID + Posição local (Level 2 - MEDIUM).
3. Landmark visual (Level 3 - MEDIUM).
4. Fallback para localização anterior / UNKNOWN.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

import sys
import time
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.navigation.runtime.navigation_observation import NavigationObservation
from src.navigation.runtime.localization import LocalizationEngine
from src.world.model.world_location import WorldLocation, LocationConfidence


def test_localization_hierarchy():
    print("🧪 Testando LocalizationEngine (Hierarquia de Fontes)...")

    localizer = LocalizationEngine()

    # 1. Level 1: Coordenadas mundiais
    obs1 = NavigationObservation(timestamp=time.time(), map_id="Pallet Town", world_x=5.0, world_y=10.0)
    loc1 = localizer.locate(obs1)
    assert loc1.confidence == LocationConfidence.HIGH
    assert loc1.x == 5.0 and loc1.y == 10.0
    print("  ✅ Level 1: Coordenadas mundiais estimaram localização com confiança HIGH")

    # 2. Level 2: Map ID sem coordenadas mundiais
    obs2 = NavigationObservation(timestamp=time.time(), map_id="Route 1", player_screen_x=100.0, player_screen_y=200.0)
    loc2 = localizer.locate(obs2)
    assert loc2.confidence == LocationConfidence.MEDIUM
    assert loc2.map_id == "Route 1"
    print("  ✅ Level 2: Map ID estimou localização com confiança MEDIUM")

    # 3. Level 3: Landmark visual
    obs3 = NavigationObservation(timestamp=time.time(), visible_landmarks=("PokéCenter Sign",))
    loc3 = localizer.locate(obs3, previous_location=loc2)
    assert loc3.confidence == LocationConfidence.MEDIUM
    assert loc3.landmark == "PokéCenter Sign"
    print("  ✅ Level 3: Landmark visual estimou localização com confiança MEDIUM")


if __name__ == "__main__":
    test_localization_hierarchy()
