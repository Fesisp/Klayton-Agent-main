"""
Subsystem State - Estados Formais de Subsistemas
=================================================

Enumeração dos estados de saúde e operacionalidade dos subsistemas.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

from enum import Enum


class SubsystemState(Enum):
    """Estados de ciclo de vida e saúde de um subsistema."""
    STOPPED = "stopped"
    STARTING = "starting"
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILED = "failed"
    RECOVERING = "recovering"
    STOPPING = "stopping"
