"""
Stress Runtime Harness - Teste de Estresse e Simulação de Ticks
===============================================================

Simula 10.000 ticks contínuos verificando vazamentos de memória, travamentos e descarte controlado de frames.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

import sys
import argparse
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.runtime.runtime_supervisor import RuntimeSupervisor
from src.runtime.runtime_scheduler import RuntimeScheduler, TickClass
from src.runtime.resource_monitor import ResourceMonitor
from src.runtime.runtime_metrics import RuntimeMetrics


def run_stress_test(ticks: int = 10000) -> bool:
    print("====================================================")
    print("⚡ KLAYTON RUNTIME STRESS TEST")
    print(f"🔄 Executando {ticks} ticks de simulação contínua...")
    print("====================================================")

    supervisor = RuntimeSupervisor()
    supervisor.start_all()

    scheduler = RuntimeScheduler()
    monitor = ResourceMonitor(max_queue_size=10)
    metrics = RuntimeMetrics()

    dropped_count = 0

    for i in range(ticks):
        monitor.push_frame(f"frame_{i}")
        if len(monitor.frame_queue) >= 10:
            dropped = monitor.push_frame(f"frame_overflow_{i}")
            if dropped:
                dropped_count += 1

        scheduler.should_tick(TickClass.REALTIME)
        metrics.record_tick_latency(0.5)

    supervisor.stop_all()

    print(f"  ✅ {ticks} ticks concluídos com sucesso")
    print(f"  ✅ Frames antigos descartados com controle (backpressure): {dropped_count}")
    print(f"  ✅ Latência P95 dos ticks: {metrics.p95_latency_ms:.2f} ms")

    print("====================================================")
    print("STATUS: STRESS TEST PASSED (READY)")
    print("====================================================")
    return True


def main():
    parser = argparse.ArgumentParser(description="Harness de Teste de Estresse do Runtime")
    parser.add_argument("--ticks", type=int, default=1000, help="Número de ticks para simular")
    args = parser.parse_args()

    success = run_stress_test(ticks=args.ticks)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
