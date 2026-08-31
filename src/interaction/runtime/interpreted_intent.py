"""
Interpreted Intent - Representação Estruturada da Intenção do Usuário
=====================================================================

Intenção interpretada a partir de frases em linguagem natural ou comandos de voz.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional


class IntentType(Enum):
    """Tipos formais de intenção humana."""
    COMMAND = "command"
    QUESTION = "question"
    CORRECTION = "correction"
    TEACHING = "teaching"
    STOP = "stop"
    PAUSE = "pause"
    RESUME = "resume"
    STATUS = "status"
    EXPLANATION = "explanation"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class InterpretedIntent:
    """Intenção estruturada interpretada."""
    type: IntentType

    action: Optional[str] = None
    target: Optional[str] = None

    parameters: Dict[str, Any] = field(default_factory=dict)

    confidence: float = 0.0

    requires_confirmation: bool = False
    ambiguous: bool = False
