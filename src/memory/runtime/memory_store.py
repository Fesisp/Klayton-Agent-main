"""
Memory Store - Repositório Persistente SQLite de Memória
=========================================================

Gerencia a persistência atômica e versionada da memória em data/runtime/memory/memory.sqlite.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
from .memory_record import MemoryRecord
from .memory_type import MemoryType
from .provenance import EvidenceSource

CURRENT_SCHEMA_VERSION = "1.0"


class MemoryStore:
    """Repositório transacional SQLite de memória."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or Path(__file__).resolve().parent.parent.parent.parent / "data" / "runtime" / "memory" / "memory.sqlite"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS schema_info (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS memory_records (
                    id TEXT PRIMARY KEY,
                    type TEXT NOT NULL,
                    key TEXT NOT NULL,
                    value_json TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    source TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL,
                    observations INTEGER NOT NULL,
                    tags_json TEXT NOT NULL,
                    metadata_json TEXT NOT NULL,
                    superseded_by TEXT
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS procedure_stats (
                    key TEXT PRIMARY KEY,
                    attempts INTEGER NOT NULL,
                    successes INTEGER NOT NULL,
                    failures INTEGER NOT NULL,
                    average_cost REAL NOT NULL,
                    average_duration REAL NOT NULL,
                    last_used REAL
                )
            """)

            cursor.execute("INSERT OR REPLACE INTO schema_info (key, value) VALUES ('schema_version', ?)", (CURRENT_SCHEMA_VERSION,))
            conn.commit()

    def save_record(self, record: MemoryRecord) -> None:
        """Salva ou atualiza atomicamente um registro de memória."""
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO memory_records (
                    id, type, key, value_json, confidence, source, created_at, updated_at, observations, tags_json, metadata_json, superseded_by
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                record.id,
                record.type.value,
                record.key,
                json.dumps(record.value, ensure_ascii=False),
                record.confidence,
                record.source.value,
                record.created_at,
                record.updated_at,
                record.observations,
                json.dumps(list(record.tags), ensure_ascii=False),
                json.dumps(record.metadata, ensure_ascii=False),
                record.superseded_by
            ))
            conn.commit()

    def get_record_by_id(self, record_id: str) -> Optional[MemoryRecord]:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM memory_records WHERE id = ?", (record_id,))
            row = cursor.fetchone()
            if row:
                return self._row_to_record(row)
        return None

    def find_records_by_key(self, key: str, memory_type: Optional[MemoryType] = None) -> List[MemoryRecord]:
        results = []
        with self._get_conn() as conn:
            cursor = conn.cursor()
            if memory_type:
                cursor.execute("SELECT * FROM memory_records WHERE key = ? AND type = ? AND superseded_by IS NULL", (key, memory_type.value))
            else:
                cursor.execute("SELECT * FROM memory_records WHERE key = ? AND superseded_by IS NULL", (key,))
            for row in cursor.fetchall():
                results.append(self._row_to_record(row))
        return results

    def list_all_records(self, memory_type: Optional[MemoryType] = None) -> List[MemoryRecord]:
        results = []
        with self._get_conn() as conn:
            cursor = conn.cursor()
            if memory_type:
                cursor.execute("SELECT * FROM memory_records WHERE type = ? AND superseded_by IS NULL", (memory_type.value,))
            else:
                cursor.execute("SELECT * FROM memory_records WHERE superseded_by IS NULL")
            for row in cursor.fetchall():
                results.append(self._row_to_record(row))
        return results

    def _row_to_record(self, row: sqlite3.Row) -> MemoryRecord:
        return MemoryRecord(
            id=row["id"],
            type=MemoryType(row["type"]),
            key=row["key"],
            value=json.loads(row["value_json"]),
            confidence=row["confidence"],
            source=EvidenceSource(row["source"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            observations=row["observations"],
            tags=set(json.loads(row["tags_json"])),
            metadata=json.loads(row["metadata_json"]),
            superseded_by=row["superseded_by"]
        )
