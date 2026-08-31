"""
Teste Rigoroso do WorldState Sync - Klayton Companion Agent
===========================================================

Garante que observações com a categoria 'world_sync' atualizam
efetivamente todos os ramos do WorldState (battle, location, resources).

Autor: Klayton Companion Agent Framework
Data: 2026-08-30
"""

import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.world.world_state import WorldState, Observation


def test_world_sync_observation_application():
    print("🧪 Testando Aplicação Real da Observação 'world_sync' no WorldState...")
    world = WorldState()

    # Emite observação com categoria world_sync
    obs = Observation(
        category="world_sync",
        data={
            "in_battle": True,
            "is_shiny": False,
            "current_map": "Viridian Forest",
            "pokeballs_count": 42,
            "potions_count": 15,
            "position": (12, 34)
        },
        confidence=0.95
    )

    applied = world.apply_observation(obs)
    assert applied is True

    # Assevera atualização real de todos os ramos
    assert world.battle.in_battle is True
    assert world.location.current_map == "Viridian Forest"
    assert world.resources.pokeballs_count == 42
    assert world.resources.potions_count == 15
    assert world.player.position == (12, 34)

    print("  ✅ Bug corrigido! Categoria 'world_sync' alimentou 100% dos ramos do WorldState com sucesso!")


if __name__ == '__main__':
    test_world_sync_observation_application()
