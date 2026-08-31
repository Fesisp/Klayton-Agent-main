"""
Goal Stack - Pilha Gerenciadora de Metas e Interrupções
======================================================

Permite que uma meta de longo prazo seja suspensa por emergências ou comandos do usuário e retomada posteriormente.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

from typing import List, Optional
from .goal_state import GoalRuntime, GoalState


class GoalStack:
    """Pilha gerenciadora de objetivos ativos e suspensos."""

    def __init__(self):
        self.stack: List[GoalRuntime] = []

    def push(self, goal: GoalRuntime) -> None:
        """Adiciona e ativa um novo objetivo no topo da pilha."""
        if self.stack and self.stack[-1].state == GoalState.ACTIVE:
            self.stack[-1].state = GoalState.SUSPENDED
        goal.state = GoalState.ACTIVE
        self.stack.append(goal)

    def pop(self) -> Optional[GoalRuntime]:
        """Remove o objetivo do topo."""
        if self.stack:
            return self.stack.pop()
        return None

    def active(self) -> Optional[GoalRuntime]:
        """Retorna o objetivo no topo da pilha."""
        if self.stack:
            return self.stack[-1]
        return None

    def suspend_active(self) -> None:
        """Suspende o objetivo ativo atual."""
        if self.stack and self.stack[-1].state == GoalState.ACTIVE:
            self.stack[-1].state = GoalState.SUSPENDED

    def resume_previous(self) -> Optional[GoalRuntime]:
        """Retoma o objetivo anterior suspenso."""
        while self.stack:
            top = self.stack[-1]
            if top.state in [GoalState.COMPLETED, GoalState.FAILED, GoalState.CANCELLED]:
                self.stack.pop()
            elif top.state == GoalState.SUSPENDED:
                top.state = GoalState.ACTIVE
                return top
            elif top.state == GoalState.ACTIVE:
                return top
        return None
