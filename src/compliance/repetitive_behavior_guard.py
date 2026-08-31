"""
Repetitive Behavior Guard - Detecção de Loops Repetitivos Improdutivos
======================================================================

Monitora o histórico recente de ações para interromper loops que não geram alteração no estado do mundo.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ActionRecord:
    action_type: str
    target: str
    timestamp: float
    world_version: int


class RepetitiveBehaviorGuard:
    """Guarda de proteção contra loops repetitivos."""

    def __init__(self, max_identical_actions: int = 10, window_seconds: float = 30.0):
        self.max_identical_actions = max_identical_actions
        self.window_seconds = window_seconds
        self.records: List[ActionRecord] = []

    def record_action(self, action_type: str, target: str, world_version: int) -> bool:
        """Registra a ação e retorna True se um loop repetitivo for detectado."""
        now = time.time()
        self.records = [r for r in self.records if now - r.timestamp <= self.window_seconds]

        self.records.append(ActionRecord(action_type=action_type, target=target, timestamp=now, world_version=world_version))

        recent_identical = [
            r for r in self.records
            if r.action_type == action_type and r.target == target
        ]

        if len(recent_identical) >= self.max_identical_actions:
            versions = {r.world_version for r in recent_identical}
            # Se o estado do mundo não mudou durante as repetições -> Loop Detectado
            if len(versions) <= 1:
                return True

        return False
