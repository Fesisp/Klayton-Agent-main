"""
Test Runtime Scheduler - Agendamento de Ticks
=============================================

Valida limites de frequência por classe de tick (REALTIME, FAST, NORMAL, BACKGROUND).

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

import sys
import time
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.runtime.runtime_scheduler import RuntimeScheduler, TickClass


def test_runtime_scheduler_intervals():
    print("🧪 Testando RuntimeScheduler (Agendamento de Frequências)...")

    scheduler = RuntimeScheduler()
    now = time.time()

    assert scheduler.should_tick(TickClass.REALTIME, now=now) is True
    assert scheduler.should_tick(TickClass.REALTIME, now=now + 0.01) is False
    assert scheduler.should_tick(TickClass.REALTIME, now=now + 0.04) is True
    print("  ✅ Agendamento de classe REALTIME respeitou o intervalo de 33 ms")


if __name__ == "__main__":
    test_runtime_scheduler_intervals()
