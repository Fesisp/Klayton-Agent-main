"""
Task Graph - Grafo de Tarefas de Longo Alcance
===============================================

Orquestra sub-tarefas com dependências encadeadas e resolve qual a próxima tarefa pronta para execução.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

from typing import Dict, List, Optional
from .task_node import TaskNode
from .task_status import TaskStatus


class TaskGraph:
    """Grafo de tarefas dependentes de longo alcance."""

    def __init__(self):
        self.nodes: Dict[str, TaskNode] = {}

    def add_task(self, task: TaskNode) -> None:
        self.nodes[task.id] = task

    def get_next_ready_task(self) -> Optional[TaskNode]:
        """Retorna a primeira sub-tarefa cujas dependências foram concluídas."""
        for task in self.nodes.values():
            if task.status in [TaskStatus.COMPLETED, TaskStatus.SKIPPED, TaskStatus.FAILED, TaskStatus.BLOCKED]:
                continue

            deps_satisfied = True
            for dep_id in task.dependencies:
                dep_node = self.nodes.get(dep_id)
                if not dep_node or dep_node.status != TaskStatus.COMPLETED:
                    deps_satisfied = False
                    break

            if deps_satisfied:
                if task.status == TaskStatus.PENDING:
                    task.status = TaskStatus.READY
                return task

        return None

    def is_complete(self) -> bool:
        if not self.nodes:
            return False
        return all(n.status in [TaskStatus.COMPLETED, TaskStatus.SKIPPED] for n in self.nodes.values())

    def is_blocked(self) -> bool:
        return any(n.status == TaskStatus.BLOCKED for n in self.nodes.values())
