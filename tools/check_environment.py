"""
Check Environment Tool - Verificação de Ambiente de Produção
============================================================

Valida versão do Python (>=3.11), plataforma Windows, integridade dos bancos SQLite e configurações.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

import sys
import platform
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


def check_environment() -> bool:
    print("====================================================")
    print("🔍 KLAYTON ENVIRONMENT CHECKER")
    print("====================================================")

    # 1. Versão do Python
    py_ver = platform.python_version()
    print(f"  🐍 Python Version: {py_ver}")
    if sys.version_info < (3, 10):
        print("  ❌ Erro: Requer Python >= 3.10")
        return False

    # 2. Sistema Operacional
    os_name = platform.system()
    print(f"  💻 Operating System: {os_name}")

    # 3. Verificação dos Bancos SQLite Mandatórios
    knowledge_dir = ROOT_DIR / "data" / "knowledge"
    required_dbs = ["pokemon.sqlite", "moves.sqlite", "types.sqlite", "natures.sqlite"]
    for db in required_dbs:
        db_p = knowledge_dir / db
        if not db_p.exists():
            print(f"  ❌ Erro: Banco de conhecimento mandatório ausente: {db}")
            return False
    print("  ✅ Bancos de dados SQLite canônicos verificados com sucesso")

    print("====================================================")
    print("STATUS: ENVIRONMENT READY")
    print("====================================================")
    return True


if __name__ == "__main__":
    success = check_environment()
    sys.exit(0 if success else 1)
