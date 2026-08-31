"""
Battle Recorder - Gravador de Sessões de Combate
================================================

Persiste a sessão de combate em formato JSON em data/runtime/battles/ para auditoria e replay.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Optional
from .battle_session import BattleSession


class BattleRecorder:
    """Gravador de sessões de combate em formato JSON."""

    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or Path(__file__).resolve().parent.parent.parent.parent / "data" / "runtime" / "battles"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def save_session(self, session: BattleSession) -> Path:
        """Salva a sessão em JSON no diretório de runtime."""
        session.ended_at = session.ended_at or time.time()
        file_path = self.output_dir / f"battle_{session.id}.json"

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(session.to_dict(), f, indent=2, ensure_ascii=False)

        return file_path
