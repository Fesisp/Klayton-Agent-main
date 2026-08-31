"""
Test Memory Store - Persistência SQLite de Memória
===================================================

Valida salvamento, recuperação por ID e por chave no repositório SQLite em data/runtime/memory/memory.sqlite.

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


def test_memory_store_sqlite():
    print("🧪 Testando MemoryStore (Persistência SQLite)...")

    with tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False) as tmp:
        db_path = Path(tmp.name)

    store = MemoryStore(db_path=db_path)
    rec = MemoryRecord(type=MemoryType.SEMANTIC, key="nurse_joy_pallet", value="healing_npc", confidence=0.95)

    store.save_record(rec)
    fetched = store.get_record_by_id(rec.id)

    assert fetched is not None
    assert fetched.key == "nurse_joy_pallet"
    assert fetched.value == "healing_npc"
    print("  ✅ Registro gravado e recuperado no banco SQLite com sucesso")


if __name__ == "__main__":
    test_memory_store_sqlite()
