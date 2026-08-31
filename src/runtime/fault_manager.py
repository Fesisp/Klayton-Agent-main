"""
Fault Manager - Gerenciador e Classificador de Falhas em Runtime
================================================================

Registra, classifica e gerencia falhas do sistema (TRANSIENT, RECOVERABLE, DEGRADED, FATAL).

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from .subsystem_state import SubsystemState


@dataclass
class RuntimeFault:
    """Registro estruturado de falha de runtime."""
    source: str
    category: str
    severity: str  # TRANSIENT, RECOVERABLE, DEGRADED, FATAL

    message: str
    timestamp: float = field(default_factory=time.time)

    recoverable: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


class FaultManager:
    """Classificador e gerenciador central de falhas."""

    def __init__(self):
        self.fault_history: List[RuntimeFault] = []
        self.active_faults: Dict[str, RuntimeFault] = {}

    def raise_fault(self, fault: RuntimeFault) -> SubsystemState:
        """Registra uma falha e retorna o novo estado recomendado para o subsistema."""
        self.fault_history.append(fault)
        self.active_faults[fault.source] = fault

        if fault.severity.upper() == "FATAL":
            return SubsystemState.FAILED
        elif fault.severity.upper() == "DEGRADED":
            return SubsystemState.DEGRADED
        elif fault.severity.upper() == "RECOVERABLE":
            return SubsystemState.RECOVERING

        return SubsystemState.HEALTHY

    def clear_fault(self, source: str) -> None:
        if source in self.active_faults:
            del self.active_faults[source]
