"""
Ambiguity Resolver - Resolução de Ambiguidade e Pedidos de Esclarecimento
=========================================================================

Decide se a ambiguidade exige pedido de esclarecimento ou pode ser resolvida pelo contexto.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

from typing import Optional, Tuple
from .interpreted_intent import InterpretedIntent


class AmbiguityResolver:
    """Resolvedor de ambiguidade que solicita esclarecimento apenas quando necessário."""

    def resolve_or_clarify(self, intent: InterpretedIntent) -> Tuple[bool, Optional[str]]:
        """
        Retorna (requires_clarification: bool, clarification_prompt: Optional[str]).
        """
        if not intent.ambiguous:
            return False, None

        if intent.action == "SWITCH":
            return True, "Qual Pokémon você gostaria de colocar em batalha?"
        if intent.action == "NAVIGATE":
            return True, "Para qual cidade ou rota você deseja ir?"

        return False, None
