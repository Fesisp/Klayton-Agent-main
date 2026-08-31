"""
Task Status - Estados de Tarefas de Longo Alcance
===============================================

Enumeração de estados das sub-tarefas de um TaskGraph.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

from enum import Enum


class TaskStatus(Enum):
    """Estados formais de uma sub-tarefa."""
    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    SUSPENDED = "suspended"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"
    SKIPPED = "skipped"
