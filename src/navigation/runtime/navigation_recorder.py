"""
Navigation Recorder - Gravador de Trajetórias JSON
===================================================

Persiste a sessão de navegação em JSON no diretório data/runtime/navigation/.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Optional
from .navigation_session import NavigationSession


class NavigationRecorder:
    """Gravador de sessões de navegação."""

    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or Path(__file__).resolve().parent.parent.parent.parent / "data" / "runtime" / "navigation"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def save_session(self, session: NavigationSession) -> Path:
        session.ended_at = session.ended_at or time.time()
        file_path = self.output_dir / f"navigation_{session.id}.json"

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(session.to_dict(), f, indent=2, ensure_ascii=False)

        return file_path
