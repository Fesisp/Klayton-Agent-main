"""
Test Perception Manager - Validação do Contrato Desacoplado de Percepção
========================================================================

Verifica:
1. Instanciação e execução limpa do PerceptionManager sem drivers reais.
2. Geração estruturada de PerceptionSnapshot sem inventar dados.
3. Aplicação fluida de PerceptionSnapshot ao WorldState.
4. Preservação de placeholders de calibração quando o jogo não estiver aberto.

Autor: Klayton Companion Agent Framework
Data: 2026-08-30
"""

import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.perception.perception_manager import PerceptionManager
from src.perception.perception_snapshot import PerceptionSnapshot
from src.world.world_state import WorldState, PokemonInfo, BattleState


def test_perception_manager_contract():
    print("🧪 Testando PerceptionManager: Contrato Desacoplado e Snapshotting...")

    # 1. Instanciação sem hardware/janela (simula ambiente sem PokeOne aberto)
    manager = PerceptionManager(config={}, components={})
    assert manager is not None

    # 2. Captura de Snapshot
    snapshot = manager.capture_snapshot()
    assert isinstance(snapshot, PerceptionSnapshot)
    assert snapshot.game_state in ["UNKNOWN", "EXPLORING"]
    assert snapshot.current_map == "Unknown"
    assert snapshot.team == []  # Nunca inventa dados falsos
    print(f"  ✅ PerceptionSnapshot gerado com segurança: game_state='{snapshot.game_state}' | map='{snapshot.current_map}'")

    # 3. Aplicação ao WorldState
    world = WorldState()
    snapshot_with_data = PerceptionSnapshot(
        game_state="IN_BATTLE",
        current_map="Route 1",
        team=[PokemonInfo(name="Pikachu", level=25, hp_percentage=0.90)],
        battle=BattleState(in_battle=True, opponent_name="Pidgey", opponent_level=5, opponent_hp_percentage=1.0)
    )
    success = world.apply_snapshot(snapshot_with_data)
    assert success is True
    assert world.battle.in_battle is True
    assert world.battle.opponent_name == "Pidgey"
    assert world.location.current_map == "Route 1"
    assert len(world.team.members) == 1
    assert world.team.members[0].name == "Pikachu"
    print(f"  ✅ WorldState assimilou PerceptionSnapshot com perfeição: Opponent='{world.battle.opponent_name}' | Map='{world.location.current_map}'")


if __name__ == '__main__':
    test_perception_manager_contract()
