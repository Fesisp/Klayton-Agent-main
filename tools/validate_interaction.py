"""
Interaction Replay Validation Harness
======================================

Validador de interpretação de intenções e resolução de comandos do usuário via replay determinístico.
Exige Command Resolution Rate >= 90.0%.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

import sys
import json
import argparse
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.interaction.runtime.interaction_context import InteractionContext
from src.interaction.runtime.context_resolver import ContextResolver
from src.interaction.runtime.interaction_metrics import InteractionMetrics


def run_interaction_validation(replay_path: Path) -> bool:
    print("====================================================")
    print("💬 KLAYTON INTERACTION REPLAY VALIDATION")
    print(f"📁 Replay File: {replay_path.name}")
    print("====================================================")

    if not replay_path.exists():
        print(f"❌ Erro: Arquivo de replay ausente em {replay_path}")
        return False

    with open(replay_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    resolver = ContextResolver()
    metrics = InteractionMetrics()

    user_cmd = data.get("user_command", "volta pra cidade")
    ctx_dict = data.get("context", {})

    context = InteractionContext(
        current_map=ctx_dict.get("current_map", "Route 1"),
        in_battle=ctx_dict.get("in_battle", False),
        active_goal_type=ctx_dict.get("active_goal_type", "TRAIN_POKEMON")
    )

    metrics.commands_received += 1
    intent = resolver.resolve(user_cmd, context)

    expected = data.get("expected", {})
    resolved = (intent.type.value == expected.get("intent_type") and intent.action == expected.get("action"))

    if resolved:
        metrics.commands_resolved += 1

    rate = metrics.command_resolution_rate * 100
    print(f"💬 Comando '{user_cmd}' -> Intenção: Type={intent.type.value}, Action={intent.action} (Resolvido={resolved})")
    print("----------------------------------------------------")
    print(f"📈 Taxa de Resolução de Comandos: {rate:.1f}% (Meta Mínima: 90.0%)")
    print("----------------------------------------------------")

    if rate >= 90.0:
        print("STATUS: INTERACTION REPLAY VALIDATED (READY)")
        return True
    else:
        print("STATUS: INTERACTION REPLAY FAILED")
        return False


def main():
    parser = argparse.ArgumentParser(description="Validador de Interação e Orientação Humana do Klayton")
    parser.add_argument("--replay", type=str, default=str(ROOT_DIR / "tests" / "fixtures" / "interaction" / "user_override.json"), help="Caminho do arquivo de replay JSON")
    args = parser.parse_args()

    success = run_interaction_validation(Path(args.replay))
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
