"""
Test Loop Detector - Detecção de Repetições Infinitas
=====================================================

Valida:
1. Acúmulo de etapas idênticas sem alteração de progresso.
2. Sinalização de LOOP DETECTED ao atingir o limite.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.agent.autonomy.loop_detector import LoopDetector


def test_loop_detector_trigger():
    print("🧪 Testando LoopDetector (Bloqueio de Repetição)...")

    detector = LoopDetector(loop_threshold=4)

    assert detector.record_step("t1", 0.5) is False
    assert detector.record_step("t1", 0.5) is False
    assert detector.record_step("t1", 0.5) is False
    loop_detected = detector.record_step("t1", 0.5)

    assert loop_detected is True
    print("  ✅ 4 repetições idênticas dispararam a trava LOOP DETECTED com sucesso")


if __name__ == "__main__":
    test_loop_detector_trigger()
