"""
Test Watchdog - Verificação de Heartbeats e Timeout
===================================================

Valida o registro de heartbeats e detecção de travamento em subsistemas após exceder o limite.

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

from src.runtime.watchdog import Watchdog


def test_watchdog_heartbeat():
    print("🧪 Testando Watchdog (Monitoramento de Heartbeats)...")

    watchdog = Watchdog(timeout_seconds=2.0)
    now = time.time()

    watchdog.heartbeat("perception")
    assert watchdog.check_subsystem("perception", now=now) is True
    print("  ✅ Heartbeat recente verificado com sucesso")

    assert watchdog.check_subsystem("perception", now=now + 5.0) is False
    print("  ✅ Timeout de heartbeat detectado após 5 segundos de inatividade")


if __name__ == "__main__":
    test_watchdog_heartbeat()
