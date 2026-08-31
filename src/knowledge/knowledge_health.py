"""
Knowledge Health Checker - Validador de Integridade da Knowledge Base
======================================================================

Valida a existência, o tamanho em disco e os quantitativos mínimos de registros
de cada banco SQLite em data/knowledge/, prevenindo arquivos corrompidos ou zerados.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any, Optional


@dataclass(frozen=True)
class DatabaseRequirement:
    filename: str
    table: str
    min_rows: int
    required: bool = True


REQUIREMENTS = [
    DatabaseRequirement("pokemon.sqlite", "pokemon", 800, required=True),
    DatabaseRequirement("moves.sqlite", "moves", 500, required=True),
    DatabaseRequirement("types.sqlite", "type_chart", 324, required=True),
    DatabaseRequirement("natures.sqlite", "natures", 25, required=True),
    DatabaseRequirement("items.sqlite", "items", 1, required=True),
    DatabaseRequirement("abilities.sqlite", "abilities", 1, required=True),
    DatabaseRequirement("evolutions.sqlite", "evolutions", 1, required=True),
    DatabaseRequirement("status_conditions.sqlite", "status_conditions", 1, required=True),
    DatabaseRequirement("hms_field_moves.sqlite", "field_moves", 1, required=True),
    DatabaseRequirement("npcs.sqlite", "npcs", 1, required=False),
    DatabaseRequirement("pokeone_encounters.sqlite", "encounters", 1, required=False),
]


class KnowledgeHealthChecker:
    """Validador de integridade dos bancos de dados SQLite da Knowledge Base."""

    def __init__(self, directory: Optional[Path] = None):
        self.directory = directory or Path(__file__).resolve().parent.parent.parent / "data" / "knowledge"

    def validate(self) -> List[str]:
        """
        Executa a verificação completa e retorna lista de mensagens de erro.
        """
        errors: List[str] = []

        if not self.directory.exists():
            return [f"Diretório de conhecimento ausente: {self.directory}"]

        for req in REQUIREMENTS:
            path = self.directory / req.filename

            if not path.exists():
                if req.required:
                    errors.append(f"CRITICAL: {req.filename} está ausente")
                else:
                    errors.append(f"WARNING: {req.filename} está ausente (opcional)")
                continue

            if path.stat().st_size == 0:
                errors.append(f"CRITICAL: {req.filename} possui 0 bytes (arquivo zerado)")
                continue

            try:
                uri = f"{path.resolve().as_uri()}?mode=ro"
                conn = sqlite3.connect(uri, uri=True)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                cursor.execute(f'SELECT COUNT(*) FROM "{req.table}"')
                row = cursor.fetchone()
                count = int(row[0]) if row else 0
                conn.close()

                if count < req.min_rows:
                    msg = f"{req.filename}/{req.table}: {count} registros (mínimo esperado: {req.min_rows})"
                    if req.required:
                        errors.append(f"CRITICAL: {msg}")
                    else:
                        errors.append(f"WARNING: {msg}")

            except Exception as exc:
                errors.append(f"ERROR: {req.filename}: {exc}")

        return errors
