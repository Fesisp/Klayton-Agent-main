"""
Test Ambiguity Resolver - Identificação de Ambiguidade e Esclarecimentos
========================================================================

Valida geração de pedidos de esclarecimento quando a ambiguidade altera materialmente a ação.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.interaction.runtime.interpreted_intent import InterpretedIntent, IntentType
from src.interaction.runtime.ambiguity_resolver import AmbiguityResolver


def test_ambiguity_resolver_prompts():
    print("🧪 Testando AmbiguityResolver (Pedidos de Esclarecimento)...")

    resolver = AmbiguityResolver()

    # 1. Intenção não ambígua
    intent_clear = InterpretedIntent(type=IntentType.COMMAND, action="RETURN_TO_CITY", ambiguous=False)
    req1, prompt1 = resolver.resolve_or_clarify(intent_clear)
    assert req1 is False
    print("  ✅ Intenção não ambígua executada sem pedir esclarecimento desnecessário")

    # 2. Intenção ambígua de troca em batalha
    intent_amb = InterpretedIntent(type=IntentType.COMMAND, action="SWITCH", ambiguous=True)
    req2, prompt2 = resolver.resolve_or_clarify(intent_amb)
    assert req2 is True
    assert "Qual Pokémon" in prompt2
    print("  ✅ Ambiguidade de troca em batalha gerou pedido de esclarecimento adequado")


if __name__ == "__main__":
    test_ambiguity_resolver_prompts()
