"""
Test Correction Handler - Processamento de Correções do Usuário
================================================================

Valida o tratamento de correções do usuário, substituindo o fato anterior via superseded_by.

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

from src.memory.memory_facade import MemoryFacade
from src.memory.runtime.memory_store import MemoryStore
from src.interaction.runtime.correction_handler import CorrectionHandler


def test_correction_handler_supersede():
    print("🧪 Testando CorrectionHandler (Aplicação de Correções)...")

    with tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False) as tmp:
        memory = MemoryFacade(store=MemoryStore(db_path=Path(tmp.name)))

    memory.record_fact_candidate("npc_route_1_role", "SHOP", confidence=0.70)
    handler = CorrectionHandler(memory_facade=memory)

    res = handler.apply_correction("npc_route_1_role", "HEAL")
    assert res["status"] == "correction_applied"
    assert res["corrected_value"] == "HEAL"
    print("  ✅ Correção aplicada com sucesso substituindo a verdade anterior")


if __name__ == "__main__":
    test_correction_handler_supersede()
