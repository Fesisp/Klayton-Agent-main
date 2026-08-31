"""
Test Teaching Interpreter - Processamento de Ensinamentos Humanos
==================================================================

Valida a conversão de ensinamentos humanos em registros da MemoryFacade com proveniência USER_CONFIRMED.

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
from src.interaction.runtime.teaching_interpreter import TeachingInterpreter


def test_teaching_interpreter_to_memory():
    print("🧪 Testando TeachingInterpreter (Registro de Ensinamentos)...")

    with tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False) as tmp:
        memory = MemoryFacade(store=MemoryStore(db_path=Path(tmp.name)))

    interpreter = TeachingInterpreter(memory_facade=memory)
    res = interpreter.process_teaching(key="npc_nurse_joy_role", value="HEAL")

    assert res["status"] == "fact_learned"
    assert res["source"] == "user_confirmed"
    assert res["confidence"] == 0.98
    print("  ✅ Ensinamento humano registrado na MemoryFacade com proveniência 'user_confirmed' (0.98)")


if __name__ == "__main__":
    test_teaching_interpreter_to_memory()
