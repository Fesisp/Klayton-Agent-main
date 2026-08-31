"""
Command Router - Roteador Estruturado de Comandos
=================================================

Converte intenções interpretadas em instâncias de metas (GoalCandidate source='user') ou sinais de pausa/retomada.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

from typing import Any, Dict, Optional
from .interpreted_intent import InterpretedIntent, IntentType


class CommandRouter:
    """Roteador estruturado de comandos para a camada de autonomia."""

    def route(self, intent: InterpretedIntent, goal_manager: Any) -> Dict[str, Any]:
        """Processa a intenção e atualiza o estado de metas sem injetar inputs físicos brutos."""
        if intent.type == IntentType.PAUSE:
            if hasattr(goal_manager, 'autonomy_controller'):
                goal_manager.autonomy_controller.stack.suspend_active()
            return {"status": "paused", "message": "Autonomia pausada pelo usuário"}

        if intent.type == IntentType.RESUME:
            if hasattr(goal_manager, 'autonomy_controller'):
                goal_manager.autonomy_controller.stack.resume_previous()
            return {"status": "resumed", "message": "Autonomia retomada"}

        if intent.type == IntentType.COMMAND:
            # Roteia o comando criando uma meta de usuário com prioridade alta
            if intent.action == "RETURN_TO_CITY":
                return {"status": "goal_created", "goal_type": "RETURN_TO_CITY", "source": "user", "target": intent.target}

        return {"status": "unhandled", "intent_type": intent.type.value}
