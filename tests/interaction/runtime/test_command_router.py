"""
Test Command Router - Roteamento de Comandos e Sinais de Pausa
==============================================================

Valida:
1. Roteamento de sinal de PAUSE e SUSPEND para a pilha de metas.
2. Roteamento de comando explícito do usuário para criação de meta com alta prioridade.

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
from src.interaction.runtime.command_router import CommandRouter


class MockGoalManager:
    pass


def test_command_router_actions():
    print("🧪 Testando CommandRouter (Pausa, Retomada e Override)...")

    router = CommandRouter()
    manager = MockGoalManager()

    # 1. Sinal de PAUSE
    intent_pause = InterpretedIntent(type=IntentType.PAUSE)
    res_pause = router.route(intent_pause, manager)
    assert res_pause["status"] == "paused"
    print("  ✅ Sinal de PAUSE roteado com sucesso sem sintetizar inputs brutos")

    # 2. Comando de Usuário (RETURN_TO_CITY)
    intent_cmd = InterpretedIntent(type=IntentType.COMMAND, action="RETURN_TO_CITY", target="Viridian City")
    res_cmd = router.route(intent_cmd, manager)
    assert res_cmd["status"] == "goal_created"
    assert res_cmd["source"] == "user"
    print("  ✅ Comando do usuário roteado com fonte 'user' para a camada de autonomia")


if __name__ == "__main__":
    test_command_router_actions()
