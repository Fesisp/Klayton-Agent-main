"""
Test Memory Consolidator - Consolidação de Episódios em Fatos
==============================================================

Valida promoção automática de episódios recorrentes para a memória semântica após 3 confirmações.

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

from src.memory.runtime.memory_record import MemoryRecord
from src.memory.runtime.memory_type import MemoryType
from src.memory.runtime.provenance import EvidenceSource
from src.memory.runtime.memory_store import MemoryStore
from src.memory.runtime.episodic_memory import EpisodicMemory
from src.memory.runtime.memory_consolidator import MemoryConsolidator


def test_memory_consolidator_promotion():
    print("🧪 Testando MemoryConsolidator (Promoção por Confirmações)...")

    with tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False) as tmp:
        store = MemoryStore(db_path=Path(tmp.name))

    episodic = EpisodicMemory(store)
    consolidator = MemoryConsolidator(store)

    # 3 episódios idênticos
    for _ in range(3):
        episodic.add(MemoryRecord(key="pallet_center_heal", value=True, confidence=0.90, source=EvidenceSource.DIRECT_OBSERVATION))

    promoted = consolidator.consolidate()
    assert len(promoted) == 1
    assert promoted[0].key == "pallet_center_heal"
    assert promoted[0].type == MemoryType.SEMANTIC
    print("  ✅ 3 episódios consistentes promoveram o fato para a memória semântica com sucesso")


if __name__ == "__main__":
    test_memory_consolidator_promotion()
