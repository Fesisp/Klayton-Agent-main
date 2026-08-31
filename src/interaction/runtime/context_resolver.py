"""
Context Resolver - Resolvedor de Referências Contextuais
========================================================

Resolve pronomes e referências contextuais ("ele", "lá", "o anterior") usando o InteractionContext real.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

from typing import Optional
from .interaction_context import InteractionContext
from .interpreted_intent import InterpretedIntent, IntentType


class ContextResolver:
    """Resolvedor de referências e entidades contextuais."""

    def resolve(self, user_text: str, context: InteractionContext) -> InterpretedIntent:
        text_lower = user_text.lower().strip()

        # 1. Comandos de Controle (PAUSE, RESUME, STOP, STATUS)
        if text_lower in ["para", "pausa", "segura", "stop", "pare"]:
            return InterpretedIntent(type=IntentType.PAUSE, confidence=0.98)
        if text_lower in ["continua", "resume", "retoma", "vai"]:
            return InterpretedIntent(type=IntentType.RESUME, confidence=0.98)
        if "o que você está fazendo" in text_lower or "status" in text_lower or "onde estamos" in text_lower:
            return InterpretedIntent(type=IntentType.STATUS, confidence=0.95)
        if "por que" in text_lower or "por que você" in text_lower or "explicar" in text_lower:
            return InterpretedIntent(type=IntentType.EXPLANATION, confidence=0.95)

        # 2. Resolução de Referências ("ele", "lá", "troca por ele")
        if "troca por ele" in text_lower or "muda pra ele" in text_lower:
            if context.in_battle and context.last_referenced_entity:
                return InterpretedIntent(type=IntentType.COMMAND, action="SWITCH", target=context.last_referenced_entity, confidence=0.90)
            elif context.in_battle:
                return InterpretedIntent(type=IntentType.COMMAND, action="SWITCH", ambiguous=True, confidence=0.50)

        # 3. Comandos de Navegação ("volta pra cidade", "vai pra cidade")
        if "volta" in text_lower or "retorne" in text_lower:
            target_map = context.current_map or "Viridian City"
            return InterpretedIntent(type=IntentType.COMMAND, action="RETURN_TO_CITY", target=target_map, confidence=0.90)

        # 4. Ensinamento / Correção ("esse npc cura", "não, ele é loja")
        if "esse npc cura" in text_lower or "nurse joy cura" in text_lower:
            return InterpretedIntent(type=IntentType.TEACHING, action="SET_NPC_ROLE", target="HEAL", confidence=0.95)
        if "não, ele é" in text_lower or "na verdade" in text_lower:
            return InterpretedIntent(type=IntentType.CORRECTION, action="UPDATE_FACT", confidence=0.90)

        return InterpretedIntent(type=IntentType.COMMAND, action="GENERIC_ACTION", confidence=0.70)
