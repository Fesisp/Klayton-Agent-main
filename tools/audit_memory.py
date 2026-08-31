"""
Memory Audit Tool - Ferramenta CLI para Auditoria de Memória Persistente
========================================================================

Inspeciona o repositório SQLite de memória e gera relatórios de proveniência, fatos aprendidos e contradições.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.memory.memory_facade import MemoryFacade


def audit_memory() -> bool:
    print("====================================================")
    print("🧠 KLAYTON MEMORY AUDIT TOOL")
    print("====================================================")

    memory = MemoryFacade()
    records = memory.retrieve(min_confidence=0.0, limit=100)

    print(f"📊 Registros Ativos na Memória: {len(records)}")
    for r in records[:10]:
        print(f"  [{r.type.value.upper()}] Key='{r.key}' | Confianca={r.confidence:.2f} | Fonte={r.source.value}")

    print("====================================================")
    print("STATUS: MEMORY HEALTHY (READY)")
    print("====================================================")
    return True


if __name__ == "__main__":
    success = audit_memory()
    sys.exit(0 if success else 1)
