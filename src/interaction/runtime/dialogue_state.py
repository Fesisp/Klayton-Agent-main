"""
Dialogue State - Estado de Diálogo Conversacional
=================================================

Mantém o histórico de mensagens recentes do usuário e agente exclusivamente para resolução de pronomes.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class DialogueState:
    """Estado leve de diálogo conversacional."""
    last_user_message: Optional[str] = None
    last_agent_response: Optional[str] = None

    pending_clarification: Optional[str] = None
    last_referenced_entity: Optional[str] = None

    active_topic: Optional[str] = None
