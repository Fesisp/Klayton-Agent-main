"""
Task Node - Nó de Tarefa em Grafo de Longo Alcance
===================================================

Representa uma etapa estruturada com dependências e status.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List
from .task_status import TaskStatus


@dataclass
class TaskNode:
    """Nó de sub-tarefa em um TaskGraph."""
    id: str
    task_type: str

    dependencies: List[str] = field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING

    attempts: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
