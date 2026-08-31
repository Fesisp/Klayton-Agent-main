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
    # 4. Teste de Extração dos Slots do Time via TeamDetector
    from src.perception.team_detector import TeamDetector
    from src.knowledge.team_manager import TeamManager
    team_mgr = TeamManager()
    team_mgr.current_team = ["pikachu", "charizard", "blastoise"]
    team_detector = TeamDetector(components={'team': team_mgr})
    slots = team_detector.detect_team_slots(frame=None, game_state="EXPLORING")
    assert len(slots) == 3
    assert slots[0].name == "Pikachu"
    assert slots[0].active is True
    assert slots[1].name == "Charizard"
    assert slots[1].active is False
    # 5. Teste de Classificação da Ação do Inimigo via Battlelog
    from src.perception.game_state_detector import GameStateDetector
    detector = GameStateDetector(None, None, {})
    assert detector.detect_enemy_action_category(battle_text="Dragonite used Dragon Dance!") == "STATUS_BUFF"
    assert detector.detect_enemy_action_category(battle_text="Blissey used Soft-Boiled!") == "HEAL"
    assert detector.detect_enemy_action_category(battle_text="Skarmory used Stealth Rock!") == "HAZARD"
    assert detector.detect_enemy_action_category(battle_text="Gengar used Hypnosis!") == "STATUS_DEBUFF"
    print("  ✅ GameStateDetector.detect_enemy_action_category classificou com perfeição as mensagens de battlelog!")


if __name__ == '__main__':
    test_perception_manager_contract()
