"""
Test Contradiction Resolver - Resolução de Contradições e Supersesão
====================================================================

Valida:
1. Marcação de superseded_by ao introduzir contradição (X=A vs X=B).
2. Prioridade de correção do usuário (USER_CONFIRMED).

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
from src.memory.runtime.contradiction_resolver import ContradictionResolver


def test_contradiction_resolver_supersession():
    print("🧪 Testando ContradictionResolver (Resolução e Supersesão)...")

    with tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False) as tmp:
        store = MemoryStore(db_path=Path(tmp.name))

    resolver = ContradictionResolver(store)

    rec1 = MemoryRecord(type=MemoryType.SEMANTIC, key="npc_1", value="shop", confidence=0.70, source=EvidenceSource.INFERRED)
    store.save_record(rec1)

    # Novo fato contraditório confirmado pelo usuário
    rec2 = MemoryRecord(type=MemoryType.SEMANTIC, key="npc_1", value="heal", confidence=0.98, source=EvidenceSource.USER_CONFIRMED)
    resolver.resolve_and_save(rec2)

    old_fetched = store.get_record_by_id(rec1.id)
    assert old_fetched.superseded_by == rec2.id
    print("  ✅ Contradição resolvida: Registro antigo marcado com superseded_by sem ser apagado silenciosamente")


if __name__ == "__main__":
    test_contradiction_resolver_supersession()
