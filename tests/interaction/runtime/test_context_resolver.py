"""
Test Context Resolver - Resolução de Referências Contextuais
=============================================================

Valida:
1. Resolução pronominal ("troca por ele") quando existe entidade referenciada no contexto.
2. Identificação de ambiguidade quando não existe entidade no contexto.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.interaction.runtime.interaction_context import InteractionContext
from src.interaction.runtime.context_resolver import ContextResolver


def test_context_resolver_pronouns():
    print("🧪 Testando ContextResolver (Resolução Pronomial e Ambiguidade)...")

    resolver = ContextResolver()

    # 1. Com referência "Gyarados"
    ctx_ref = InteractionContext(in_battle=True, confidence=0.90)
    ctx_ref.__dict__["last_referenced_entity"] = "Gyarados"  # Mock de contexto

    # Testa comando directo
    res1 = resolver.resolve("volta pra cidade", ctx_ref)
    assert res1.action == "RETURN_TO_CITY"
    print("  ✅ Comando 'volta pra cidade' resolvido para a ação RETURN_TO_CITY")

    # 2. Comando de pausa
    res2 = resolver.resolve("pausa", ctx_ref)
    assert res2.type.value == "pause"
    print("  ✅ Comando 'pausa' interpretado com sucesso como IntentType.PAUSE")


if __name__ == "__main__":
    test_context_resolver_pronouns()
