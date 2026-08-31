"""
Event Bus - Barramento de Eventos de Runtime
============================================

Fornece publicação e subscrição de eventos com sequência monotônica, timestamp e suporte a correlation_id.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional


@dataclass
class RuntimeEvent:
    """Evento de runtime com sequência e rastreamento."""
    event_type: str
    data: Dict[str, Any]
    source: str = "runtime"
    sequence_id: int = 0
    timestamp: float = field(default_factory=time.time)
    correlation_id: Optional[str] = None


class EventBus:
    """Barramento central de eventos sem recursão infinita."""

    def __init__(self):
        self._sequence_counter: int = 0
        self._listeners: Dict[str, List[Callable[[RuntimeEvent], None]]] = {}

    def subscribe(self, event_type: str, callback: Callable[[RuntimeEvent], None]) -> None:
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(callback)

    def publish(self, event_type: str, data: Dict[str, Any], source: str = "runtime", correlation_id: Optional[str] = None) -> RuntimeEvent:
        self._sequence_counter += 1
        event = RuntimeEvent(
            event_type=event_type,
            data=data,
            source=source,
            sequence_id=self._sequence_counter,
            correlation_id=correlation_id
        )

        listeners = self._listeners.get(event_type, [])
        for cb in listeners:
            try:
                cb(event)
            except Exception:
                pass

        return event
