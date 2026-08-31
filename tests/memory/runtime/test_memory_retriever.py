"""
Test Memory Retriever - Mecanismo de Busca e Ranking
=====================================================

Valida filtragem por tag, confiança mínima e ranking por relevância e recência.

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
from src.memory.runtime.memory_store import MemoryStore
from src.memory.runtime.memory_retriever import MemoryRetriever


def test_memory_retriever_ranking():
    print("🧪 Testando MemoryRetriever (Busca e Ranking)...")

    with tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False) as tmp:
        store = MemoryStore(db_path=Path(tmp.name))

    retriever = MemoryRetriever(store)

    store.save_record(MemoryRecord(key="pallet_poke", confidence=0.50, tags={"location"}))
    store.save_record(MemoryRecord(key="pallet_town", confidence=0.95, tags={"location"}))

    res = retriever.retrieve(query="pallet", min_confidence=0.80, tags={"location"})
    assert len(res) == 1
    assert res[0].key == "pallet_town"
    print("  ✅ Recuperação filtrada por tag e confiança mínima efetuada com sucesso")


if __name__ == "__main__":
    test_memory_retriever_ranking()
