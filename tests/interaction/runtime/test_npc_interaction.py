"""
Test NPC Interaction - Contexto e Verificação de Interação
==========================================================

Valida a estruturação do contexto de interação com NPC.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.interaction.runtime.npc_interaction_context import NPCInteractionContext


def test_npc_interaction_context_flow():
    print("🧪 Testando NPCInteractionContext (Contexto de Interação)...")

    ctx = NPCInteractionContext(
        npc_id="npc_nurse_joy",
        npc_name="Nurse Joy",
        map_id="Pallet Town",
        known_role="HEAL",
        confidence=0.95
    )

    assert ctx.npc_id == "npc_nurse_joy"
    assert ctx.known_role == "HEAL"
    assert ctx.confidence == 0.95
    print("  ✅ Contexto de interação com NPC configurado com sucesso")


if __name__ == "__main__":
    test_npc_interaction_context_flow()
