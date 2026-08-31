"""
Audit Knowledge Tool - Relatório de Integridade dos Bancos SQLite
==================================================================

Auditador de tabelas, contagem de linhas e verificação dos bancos de dados em data/knowledge/.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

import sys
import sqlite3
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


def audit_knowledge() -> bool:
    print("====================================================")
    print("📚 KLAYTON KNOWLEDGE DATABASE AUDIT")
    print("====================================================")

    k_dir = ROOT_DIR / "data" / "knowledge"
    dbs = ["pokemon.sqlite", "moves.sqlite", "types.sqlite", "natures.sqlite"]

    for db_name in dbs:
        db_path = k_dir / db_name
        if not db_path.exists():
            print(f"  ❌ {db_name:<20}: FAIL (Arquivo não encontrado)")
            return False

        try:
            conn = sqlite3.connect(f"{db_path.resolve().as_uri()}?mode=ro", uri=True)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall() if not row[0].startswith("sqlite_")]

            row_counts = []
            for t in tables[:3]:
                cursor.execute(f"SELECT COUNT(*) FROM {t};")
                cnt = cursor.fetchone()[0]
                row_counts.append(f"{t}: {cnt}")

            conn.close()
            print(f"  ✅ {db_name:<20}: PASS ({', '.join(row_counts)})")
        except Exception as e:
            print(f"  ❌ {db_name:<20}: FAIL ({e})")
            return False

    print("====================================================")
    print("STATUS: KNOWLEDGE HEALTH PASS")
    print("====================================================")
    return True


if __name__ == "__main__":
    success = audit_knowledge()
    sys.exit(0 if success else 1)
