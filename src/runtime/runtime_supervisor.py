"""
Runtime Supervisor - Orquestrador Central e Supervisor do Agente
=================================================================

Orquestra a ordem rigorosa de inicialização e desligamento reverso, monitorando o estado global.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

from typing import Dict, List, Optional
from .subsystem_state import SubsystemState
from .fault_manager import FaultManager
from .shutdown_manager import ShutdownManager


class RuntimeSupervisor:
    """Supervisor e orquestrador do ciclo de vida do Klayton 2.0."""

    def __init__(self):
        self.subsystem_states: Dict[str, SubsystemState] = {
            "perception": SubsystemState.STOPPED,
            "knowledge": SubsystemState.STOPPED,
            "memory": SubsystemState.STOPPED,
            "planners": SubsystemState.STOPPED,
            "execution": SubsystemState.STOPPED,
            "interaction": SubsystemState.STOPPED,
            "autonomy": SubsystemState.STOPPED,
        }
        self.fault_manager: FaultManager = FaultManager()
        self.shutdown_manager: ShutdownManager = ShutdownManager()

    def start_all(self) -> bool:
        """Inicializa subsistemas na ordem rigorosa definida."""
        startup_sequence = ["perception", "knowledge", "memory", "planners", "execution", "interaction", "autonomy"]
        for sub in startup_sequence:
            self.subsystem_states[sub] = SubsystemState.HEALTHY
        return True

    def stop_all(self) -> bool:
        """Encerra subsistemas na ordem inversa."""
        shutdown_sequence = ["autonomy", "interaction", "execution", "planners", "memory", "knowledge", "perception"]
        for sub in shutdown_sequence:
            self.subsystem_states[sub] = SubsystemState.STOPPED
        return self.shutdown_manager.shutdown()

    def is_healthy(self) -> bool:
        critical = ["perception", "execution", "autonomy"]
        return all(self.subsystem_states.get(c) in [SubsystemState.HEALTHY, SubsystemState.DEGRADED] for c in critical)
