"""
Test Resource Monitor - Filas Limitadas e Backpressure
======================================================

Valida descarte controlado de frames antigos (latest frame wins) ao exceder a fila máxima.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.runtime.resource_monitor import ResourceMonitor


def test_resource_monitor_backpressure():
    print("🧪 Testando ResourceMonitor (Filas Limitadas e Backpressure)...")

    rm = ResourceMonitor(max_queue_size=3)

    rm.push_frame("f1")
    rm.push_frame("f2")
    rm.push_frame("f3")
    dropped = rm.push_frame("f4")

    assert dropped == "f1"
    assert len(rm.frame_queue) == 3
    assert rm.get_latest_frame() == "f4"
    print("  ✅ Frame f1 descartado com controle ao exceder o limite de 3 frames")


if __name__ == "__main__":
    test_resource_monitor_backpressure()
