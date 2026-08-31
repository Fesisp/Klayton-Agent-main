"""
Test Session Guard - Duração de Sessão Contínua
===============================================

Valida a interrupção da sessão ao ultrapassar o tempo limite (ex: 60 minutos).

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

import sys
import time
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.compliance.session_guard import SessionGuard


def test_session_guard():
    print("🧪 Testando SessionGuard (Limite de Duração de Sessão)...")

    guard = SessionGuard(max_minutes=60)
    now = time.monotonic()

    assert guard.exceeded(now=now) is False
    assert guard.exceeded(now=now + 3600.0) is True
    print("  ✅ Excesso de tempo de sessão contínua (60 min) detectado corretamente")


if __name__ == "__main__":
    test_session_guard()
