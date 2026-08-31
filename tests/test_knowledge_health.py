"""
Test Knowledge Health Checker & Read-Only SQLite Integrity
===========================================================

Valida os testes de integridade da Knowledge Base:
- Detecção de arquivos SQLite ausentes ou de 0 bytes.
- Validação do fail-fast KnowledgeDatabaseError.
- Confirmação do quantitativo mínimo de registros por tabela.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

import sys
import pytest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.knowledge.knowledge_health import KnowledgeHealthChecker
from src.knowledge.knowledge_base import KnowledgeBase, KnowledgeDatabaseError


def test_knowledge_health_validation():
    print("🧪 Testando Knowledge Health Checker & Integridade SQLite...")

    checker = KnowledgeHealthChecker()
    errors = checker.validate()

    critical_errors = [e for e in errors if "CRITICAL" in e or "ERROR" in e]
    assert len(critical_errors) == 0, f"Erros críticos encontrados na Knowledge Base: {critical_errors}"
    print("  ✅ KnowledgeHealthChecker confirmou integridade das tabelas mandatórias em data/knowledge/")

    # Teste de Fail-Fast com banco ausente
    kb = KnowledgeBase()
    kb.knowledge_dir = Path("scratch/non_existent_dir_123")
    with pytest.raises(KnowledgeDatabaseError):
        kb._get_conn("fake_db")
    print("  ✅ KnowledgeBase levantou KnowledgeDatabaseError fail-fast em banco ausente")


if __name__ == "__main__":
    test_knowledge_health_validation()
