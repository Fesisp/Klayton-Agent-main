"""
Test Stuck Detector - Detecção e Severidade de Bloqueio Espacial
===============================================================

Valida:
1. Acúmulo de falhas consecutivas de progresso.
2. Atribuição de severidade (NONE ➔ SUSPECTED ➔ CONFIRMED ➔ HARD).
3. Reset imediato de severidade ao observar PROGRESS.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.navigation.runtime.navigation_progress import NavigationProgress
from src.navigation.runtime.stuck_detector import StuckDetector, StuckSeverity


def test_stuck_detector_severity():
    print("🧪 Testando StuckDetector (Severidade de Bloqueio Espacial)...")

    detector = StuckDetector(repeated_action_limit=4, hard_stuck_limit=8)

    # 1. Duas falhas -> SUSPECTED
    detector.update(NavigationProgress.NO_PROGRESS)
    s1 = detector.update(NavigationProgress.NO_PROGRESS)
    assert s1 == StuckSeverity.SUSPECTED
    print("  ✅ 2 falhas consecutivas classificadas como SUSPECTED")

    # 2. Quatro falhas -> CONFIRMED
    detector.update(NavigationProgress.NO_PROGRESS)
    s2 = detector.update(NavigationProgress.NO_PROGRESS)
    assert s2 == StuckSeverity.CONFIRMED
    print("  ✅ 4 falhas consecutivas classificadas como CONFIRMED")

    # 3. Oito falhas -> HARD
    for _ in range(4):
        detector.update(NavigationProgress.NO_PROGRESS)
    s3 = detector.update(NavigationProgress.NO_PROGRESS)
    assert s3 == StuckSeverity.HARD
    print("  ✅ 8 falhas consecutivas classificadas como HARD")

    # 4. Progresso -> Reset imediato
    s4 = detector.update(NavigationProgress.PROGRESS)
    assert s4 == StuckSeverity.NONE
    assert detector.no_progress_count == 0
    print("  ✅ Observação de PROGRESS resetou o estado de stuck para NONE")


if __name__ == "__main__":
    test_stuck_detector_severity()
