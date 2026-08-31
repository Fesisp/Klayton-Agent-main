"""
Test Fault Manager - Classificação e Transição de Falhas
=========================================================

Valida o registro de falhas e transição de estado dos subsistemas (HEALTHY ➔ DEGRADED ➔ FAILED).

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.runtime.fault_manager import FaultManager, RuntimeFault
from src.runtime.subsystem_state import SubsystemState


def test_fault_manager_classification():
    print("🧪 Testando FaultManager (Classificação de Severidade)...")

    fm = FaultManager()

    f_deg = RuntimeFault(source="tts", category="audio", severity="DEGRADED", message="TTS API offline")
    st1 = fm.raise_fault(f_deg)
    assert st1 == SubsystemState.DEGRADED
    print("  ✅ Falha de TTS classificada como DEGRADED sem derrubar o sistema principal")

    f_fat = RuntimeFault(source="perception", category="vision", severity="FATAL", message="Frame capture error")
    st2 = fm.raise_fault(f_fat)
    assert st2 == SubsystemState.FAILED
    print("  ✅ Falha crítica de percepção classificada como FAILED")


if __name__ == "__main__":
    test_fault_manager_classification()
