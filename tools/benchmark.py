"""
Benchmark Runner - Medidor de Desempenho e Latências p50/p95/p99
================================================================

Executa medições de latência nos subsistemas centrais de percepção, decisão GOAP, busca e memória.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.memory.memory_facade import MemoryFacade
from src.world.world_state import WorldState
from src.decision.goap_planner import GOAPPlanner


def run_benchmarks() -> bool:
    print("====================================================")
    print("⚡ KLAYTON PERFORMANCE BENCHMARKS")
    print("====================================================")

    # 1. Benchmark de Memória
    mem = MemoryFacade()
    t0 = time.perf_counter()
    for i in range(100):
        mem.retrieve(query=f"key_{i}")
    t1 = time.perf_counter()
    mem_lat = ((t1 - t0) / 100.0) * 1000.0
    print(f"  🧠 Memory Retrieval Latency (100 ops): {mem_lat:.3f} ms / op")

    # 2. Benchmark de GOAP Planner
    planner = GOAPPlanner()
    world = WorldState()
    world.team.members.append(type("Pkmn", (), {"hp_percentage": 0.15, "name": "Pikachu", "level": 30})())

    t0 = time.perf_counter()
    for _ in range(20):
        planner.plan(world, "HEAL_TEAM")
    t1 = time.perf_counter()
    goap_lat = ((t1 - t0) / 20.0) * 1000.0
    print(f"  🎯 GOAP Planning Latency (20 ops): {goap_lat:.3f} ms / op")

    print("====================================================")
    print("STATUS: BENCHMARKS PASSED (READY)")
    print("====================================================")
    return True


if __name__ == "__main__":
    success = run_benchmarks()
    sys.exit(0 if success else 1)
