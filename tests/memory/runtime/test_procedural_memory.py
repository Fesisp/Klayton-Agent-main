"""
Test Procedural Memory - Estatísticas de Desempenho
===================================================

Valida o rastreamento de tentativas, sucessos, falhas e cálculo de taxa de sucesso com Laplace smoothing.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

import sys
import tempfile
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.memory.runtime.memory_store import MemoryStore
from src.memory.runtime.procedural_memory import ProceduralMemory


def test_procedural_memory_stats():
    print("🧪 Testando ProceduralMemory (Estatísticas Procedurais)...")

    with tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False) as tmp:
        store = MemoryStore(db_path=Path(tmp.name))

    proc = ProceduralMemory(store)
    key = "tactic_thunderbolt_v_water"

    for _ in range(8):
        proc.record_attempt(key, success=True, duration=1.5, cost=1.0)
    for _ in range(2):
        proc.record_attempt(key, success=False, duration=2.0, cost=1.0)

    stats = proc.get_stats(key)
    assert stats.attempts == 10
    assert stats.successes == 8
    assert stats.failures == 2
    assert abs(stats.success_rate - 0.75) < 1e-4  # (8 + 1) / (10 + 2) = 9/12 = 0.75
    print("  ✅ 10 tentativas (8 sucessos / 2 falhas) calcularam taxa suavizada exata de 0.75")


if __name__ == "__main__":
    test_procedural_memory_stats()
