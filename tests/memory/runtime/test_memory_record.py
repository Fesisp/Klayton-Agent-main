"""
Test Memory Record - Estrutura e Serialização de Memória
=========================================================

Valida criação, tipo, proveniência e conversão para dicionário do MemoryRecord.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.memory.runtime.memory_record import MemoryRecord
from src.memory.runtime.memory_type import MemoryType
from src.memory.runtime.provenance import EvidenceSource


def test_memory_record_creation():
    print("🧪 Testando MemoryRecord (Estrutura e Serialização)...")

    rec = MemoryRecord(
        type=MemoryType.EPISODIC,
        key="test_key",
        value={"foo": "bar"},
        confidence=0.90,
        source=EvidenceSource.DIRECT_OBSERVATION,
        tags={"test"}
    )

    d = rec.to_dict()
    assert d["type"] == "episodic"
    assert d["key"] == "test_key"
    assert d["confidence"] == 0.90
    assert d["source"] == "direct_observation"
    print("  ✅ MemoryRecord instanciado e serializado para dicionário com sucesso")


if __name__ == "__main__":
    test_memory_record_creation()
