"""
Knowledge Base - Repositório SQLite para o Autonomous Learning System
=======================================================================

Armazena em SQLite (data/learning/knowledge.db) os fatos aprendidos (learned_facts),
eventos de experimento (learning_events) e registros de decisões (decisions).

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path
from typing import Dict, Any, Optional, List
from .models import LearnedFact, KnowledgeStatus, DecisionRecord


class KnowledgeBase:

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or Path("data/learning/knowledge.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_sqlite_schema()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_sqlite_schema(self) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS learned_facts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    concept TEXT UNIQUE NOT NULL,
                    properties_json TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    observations INTEGER NOT NULL,
                    successes INTEGER NOT NULL,
                    failures INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    source TEXT NOT NULL,
                    first_seen REAL NOT NULL,
                    last_seen REAL NOT NULL,
                    visual_reference TEXT
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS learning_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    concept TEXT NOT NULL,
                    action TEXT,
                    expectation TEXT,
                    success INTEGER,
                    confidence_before REAL,
                    confidence_after REAL,
                    reason TEXT
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS decisions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    goal TEXT NOT NULL,
                    action TEXT NOT NULL,
                    predicted_reward REAL NOT NULL,
                    predicted_risk REAL NOT NULL,
                    actual_reward REAL,
                    success INTEGER,
                    duration REAL,
                    retries INTEGER NOT NULL DEFAULT 0
                )
            """)
            conn.commit()

    def save_fact(self, fact: LearnedFact) -> None:
        now = time.time()
        fact.last_seen = now

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO learned_facts (concept, properties_json, confidence, observations, successes, failures, status, source, first_seen, last_seen, visual_reference)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(concept) DO UPDATE SET
                    properties_json = excluded.properties_json,
                    confidence = excluded.confidence,
                    observations = excluded.observations,
                    successes = excluded.successes,
                    failures = excluded.failures,
                    status = excluded.status,
                    source = excluded.source,
                    last_seen = excluded.last_seen,
                    visual_reference = excluded.visual_reference
            """, (
                fact.concept,
                json.dumps(fact.properties, ensure_ascii=False),
                fact.confidence,
                fact.observations,
                fact.successes,
                fact.failures,
                str(fact.status.value if isinstance(fact.status, KnowledgeStatus) else fact.status),
                fact.source,
                fact.first_seen,
                fact.last_seen,
                fact.visual_reference
            ))
            conn.commit()

    def find_similar(self, concept: str, properties: Optional[Dict[str, Any]] = None) -> Optional[LearnedFact]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM learned_facts WHERE concept = ?", (concept,))
            row = cursor.fetchone()
            if row:
                return self._row_to_fact(row)
        return None

    def get_fact(self, concept: str) -> Optional[LearnedFact]:
        """Alias para busca de fato por conceito."""
        return self.find_similar(concept)

    def list_facts(self) -> List[LearnedFact]:
        """Retorna a lista completa de fatos armazenados no SQLite."""
        results = []
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM learned_facts")
            for r in cursor.fetchall():
                results.append(self._row_to_fact(r))
        return results

    def get_confirmed(self, concept: str) -> List[LearnedFact]:
        results = []
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM learned_facts WHERE concept LIKE ? AND status IN ('confirmed', 'trusted')", (f"%{concept}%",))
            rows = cursor.fetchall()
            for r in rows:
                results.append(self._row_to_fact(r))
        return results

    def save_learning_event(
        self,
        concept: str,
        action: str,
        expectation: str,
        success: bool,
        confidence_before: float,
        confidence_after: float,
        reason: str
    ) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO learning_events (timestamp, concept, action, expectation, success, confidence_before, confidence_after, reason)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                time.time(),
                concept,
                action,
                expectation,
                1 if success else 0,
                confidence_before,
                confidence_after,
                reason
            ))
            conn.commit()

    def save_decision_record(self, record: DecisionRecord) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO decisions (timestamp, goal, action, predicted_reward, predicted_risk, actual_reward, success, duration, retries)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                record.timestamp,
                record.goal,
                record.action,
                record.predicted_reward,
                record.predicted_risk,
                record.actual_reward,
                1 if record.success else 0 if record.success is not None else None,
                record.duration,
                record.retries
            ))
            conn.commit()

    def _row_to_fact(self, row: sqlite3.Row) -> LearnedFact:
        st_val = str(row["status"]).lower()
        if "confirmed" in st_val:
            st_enum = KnowledgeStatus.CONFIRMED
        elif "likely" in st_val:
            st_enum = KnowledgeStatus.LIKELY
        elif "trusted" in st_val:
            st_enum = KnowledgeStatus.TRUSTED
        elif "refuted" in st_val:
            st_enum = KnowledgeStatus.REFUTED
        else:
            st_enum = KnowledgeStatus.HYPOTHESIS

        return LearnedFact(
            concept=row["concept"],
            properties=json.loads(row["properties_json"]),
            confidence=row["confidence"],
            observations=row["observations"],
            successes=row["successes"],
            failures=row["failures"],
            status=st_enum,
            source=row["source"],
            first_seen=row["first_seen"],
            last_seen=row["last_seen"],
            visual_reference=row["visual_reference"]
        )
