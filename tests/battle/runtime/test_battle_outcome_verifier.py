"""
Test Battle Outcome Verifier - Validação de Efeitos Empíricos
============================================================

Valida:
1. Input solto não confirma ação (retorna PENDING).
2. Ataque verificado por HP Delta (CONFIRMED).
3. Golpe de Status verificado por mudança de status (CONFIRMED).
4. Troca de Pokémon verificada por alteração de Pokémon ativo (CONFIRMED).
5. Troca incorreta retorna AMBIGUOUS.
6. Timeout por inércia do ambiente (TIMEOUT).

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
from src.battle.runtime.battle_action import BattleAction, BattleActionType
from src.battle.runtime.battle_event import BattleEvent, BattleEventType
from src.battle.runtime.battle_outcome_verifier import BattleOutcomeVerifier, OutcomeStatus


def test_battle_outcome_verifier_scenarios():
    print("🧪 Testando BattleOutcomeVerifier (Garantia de Ciclo Fechado)...")

    verifier = BattleOutcomeVerifier(timeout_seconds=2.0)
    now = time.time()

    obs_before = BattleObservation(timestamp=now, in_battle=True, player_pokemon="Pikachu", enemy_pokemon="Geodude", enemy_hp_ratio=1.0)

    # 1. Teste: Clique sem mudança observada -> PENDING (Não confirma só pelo input!)
    act_attack = BattleAction(type=BattleActionType.MOVE, move_slot=0)
    obs_same = BattleObservation(timestamp=now + 0.5, in_battle=True, player_pokemon="Pikachu", enemy_pokemon="Geodude", enemy_hp_ratio=1.0)
    out1 = verifier.verify(act_attack, obs_before, [obs_same], [])

    assert out1.status == OutcomeStatus.PENDING
    print("  ✅ Teste 1: Input solto sem efeito observável retornou PENDING (Ciclo Fechado Seguro)")

    # 2. Teste: Ataque verificado por HP Delta -> CONFIRMED
    obs_hit = BattleObservation(timestamp=now + 1.0, in_battle=True, player_pokemon="Pikachu", enemy_pokemon="Geodude", enemy_hp_ratio=0.5)
    ev_hit = [BattleEvent(type=BattleEventType.ENEMY_HP_CHANGED, timestamp=now + 1.0, data={"delta": -0.5}, confidence=0.95)]
    out2 = verifier.verify(act_attack, obs_before, [obs_hit], ev_hit)

    assert out2.status == OutcomeStatus.CONFIRMED
    print("  ✅ Teste 2: Ataque verificado por HP Delta retornou CONFIRMED com sucesso")

    # 3. Teste: Golpe de Status -> CONFIRMED
    ev_status = [BattleEvent(type=BattleEventType.ENEMY_STATUS_CHANGED, timestamp=now + 1.0, data={"after": "PAR"}, confidence=0.90)]
    out3 = verifier.verify(act_attack, obs_before, [obs_same], ev_status)

    assert out3.status == OutcomeStatus.CONFIRMED
    print("  ✅ Teste 3: Golpe de Status verificado por transição de status retornou CONFIRMED")

    # 4. Teste: Troca de Pokémon Correta -> CONFIRMED
    act_switch = BattleAction(type=BattleActionType.SWITCH, switch_target="Gyarados")
    obs_sw = BattleObservation(timestamp=now + 1.0, in_battle=True, player_pokemon="Gyarados", enemy_pokemon="Geodude")
    ev_sw = [BattleEvent(type=BattleEventType.PLAYER_SWITCHED, timestamp=now + 1.0, data={"after": "Gyarados"}, confidence=0.95)]
    out4 = verifier.verify(act_switch, obs_before, [obs_sw], ev_sw)

    assert out4.status == OutcomeStatus.CONFIRMED
    print("  ✅ Teste 4: Troca para Gyarados verificada e retornou CONFIRMED")

    # 5. Teste: Troca Incorreta (Alvo ambíguo)
    obs_sw_wrong = BattleObservation(timestamp=now + 1.0, in_battle=True, player_pokemon="Charizard", enemy_pokemon="Geodude")
    ev_sw_wrong = [BattleEvent(type=BattleEventType.PLAYER_SWITCHED, timestamp=now + 1.0, data={"after": "Charizard"}, confidence=0.95)]
    out5 = verifier.verify(act_switch, obs_before, [obs_sw_wrong], ev_sw_wrong)

    assert out5.status == OutcomeStatus.AMBIGUOUS
    print("  ✅ Teste 5: Troca para Pokémon não solicitado retornou AMBIGUOUS")

    # 6. Teste: Timeout
    obs_late = BattleObservation(timestamp=now + 3.0, in_battle=True, player_pokemon="Pikachu", enemy_pokemon="Geodude", enemy_hp_ratio=1.0)
    out6 = verifier.verify(act_attack, obs_before, [obs_late], [])

    assert out6.status == OutcomeStatus.TIMEOUT
    print("  ✅ Teste 6: Inércia após limite de tempo (2s) retornou TIMEOUT")


if __name__ == "__main__":
    test_battle_outcome_verifier_scenarios()
