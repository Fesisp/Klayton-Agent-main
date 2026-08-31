"""
Replay Runtime Events - Validador de Diálogo e Eventos de Runtime
=================================================================

Ferramenta para reprodução determinística da sequência de eventos do barramento EventBus.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.runtime.event_bus import EventBus


def replay_events() -> bool:
    print("====================================================")
    print("🔄 KLAYTON RUNTIME EVENT REPLAY HARNESS")
    print("====================================================")

    bus = EventBus()
    received_events = []

    bus.subscribe("BATTLE_STARTED", lambda ev: received_events.append(ev))
    bus.publish("BATTLE_STARTED", {"opponent": "Pikachu"}, source="test")

    assert len(received_events) == 1
    assert received_events[0].sequence_id == 1
    print("  ✅ Evento BATTLE_STARTED publicado e recebido em sequência determinística")

    print("====================================================")
    print("STATUS: EVENT REPLAY PASSED (READY)")
    print("====================================================")
    return True


if __name__ == "__main__":
    success = replay_events()
    sys.exit(0 if success else 1)
