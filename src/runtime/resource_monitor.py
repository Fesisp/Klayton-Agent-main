"""
Resource Monitor - Monitoramento de Recursos e Filas Limitadas
===============================================================

Monitora consumo de RAM/CPU e aplica a política de backpressure 'latest frame wins' em filas limitadas.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

from typing import Any, List, Optional


class ResourceMonitor:
    """Monitor de consumo de recursos e controlador de filas limitadas."""

    def __init__(self, max_queue_size: int = 10):
        self.max_queue_size = max_queue_size
        self.frame_queue: List[Any] = []

    def push_frame(self, frame: Any) -> Optional[Any]:
        """Aplica a política 'latest frame wins' se a fila atingir o limite máximo."""
        dropped = None
        if len(self.frame_queue) >= self.max_queue_size:
            dropped = self.frame_queue.pop(0)  # Descarta o frame mais antigo
        self.frame_queue.append(frame)
        return dropped

    def get_latest_frame(self) -> Optional[Any]:
        if self.frame_queue:
            latest = self.frame_queue.pop()
            self.frame_queue.clear()
            return latest
        return None
