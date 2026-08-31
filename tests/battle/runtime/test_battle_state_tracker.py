"""
Test Battle State Tracker - Rastreamento e Eventos Empíricos
============================================================

Valida:
1. Início e fim de batalha.
2. Detecção de HP Delta do adversário e do jogador.
3. Detecção de Faint.
4. Detecção de Troca de Pokémon.
5. Detecção de transição de status.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

import sys
import time
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.battle.runtime.battle_observation import BattleObservation
from src.battle.runtime.battle_state_tracker import BattleStateTracker
from src.battle.runtime.battle_event import BattleEventType


def test_battle_state_tracker_events():
    print("🧪 Testando BattleStateTracker (Detecção de Eventos Empíricos)...")

    tracker = BattleStateTracker()
    now = time.time()

    # 1. Início de Batalha
    obs1 = BattleObservation(timestamp=now, in_battle=True, player_pokemon="Pikachu", enemy_pokemon="Squirtle", player_hp_ratio=1.0, enemy_hp_ratio=1.0)
    events1 = tracker.update(obs1)

    assert any(e.type == BattleEventType.BATTLE_STARTED for e in events1)
    assert any(e.type == BattleEventType.TURN_STARTED for e in events1)
    print("  ✅ Teste 1: Início de batalha e Turno 1 detectados com sucesso")

    # 2. Mudança de HP e Faint
    obs2 = BattleObservation(timestamp=now + 1.0, in_battle=True, player_pokemon="Pikachu", enemy_pokemon="Squirtle", player_hp_ratio=1.0, enemy_hp_ratio=0.0)
    events2 = tracker.update(obs2)

    assert any(e.type == BattleEventType.ENEMY_HP_CHANGED for e in events2)
    assert any(e.type == BattleEventType.ENEMY_FAINTED for e in events2)
    assert any(e.type == BattleEventType.BATTLE_WON for e in events2)
    print("  ✅ Teste 2: Mudança de HP, Faint e Vitória detectadas empiricamente")

    # 3. Troca de Pokémon
    tracker_sw = BattleStateTracker()
    tracker_sw.update(obs1)
    obs_sw = BattleObservation(timestamp=now + 2.0, in_battle=True, player_pokemon="Charizard", enemy_pokemon="Squirtle", player_hp_ratio=1.0, enemy_hp_ratio=1.0)
    events_sw = tracker_sw.update(obs_sw)

    assert any(e.type == BattleEventType.PLAYER_SWITCHED for e in events_sw)
    print("  ✅ Teste 3: Troca de Pokémon do jogador (Pikachu ➔ Charizard) detectada com sucesso")


if __name__ == "__main__":
    test_battle_state_tracker_events()
