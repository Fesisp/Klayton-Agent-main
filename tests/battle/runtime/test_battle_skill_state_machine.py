"""
Test BattleSkill State Machine - Ciclo Fechado de Combate
=========================================================

Valida a execução contínua da BattleSkill em SkillStatus.RUNNING até a finalização real da batalha (SkillStatus.SUCCESS).

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

from src.skills.battle_skill import BattleSkill
from src.skills.base_skill import SkillStatus
from src.world.world_state import WorldState


class MockBattleStrategy:
    def decide_action(self, active_pkmn, enemy_pkmn, world=None):
        from src.battle.runtime.battle_action import BattleAction, BattleActionType
        from src.battle.runtime.battle_decision import BattleDecision
        act = BattleAction(type=BattleActionType.MOVE, move_slot=0)
        return BattleDecision(action=act, score=0.9, confidence=0.9, reason="Mock Attack")


class MockInputSimulator:
    def humanized_click_in_slot(self, slot: int):
        pass


def test_battle_skill_state_machine_flow():
    print("🧪 Testando BattleSkill State Machine (Ciclo Fechado de Combate)...")

    skill = BattleSkill()
    world = WorldState()
    world.battle.in_battle = True
    world.battle.opponent_name = "Charmander"

    components = {
        "strategy": MockBattleStrategy(),
        "input": MockInputSimulator()
    }

    # Step 1: ACQUIRE_STATE -> DECIDE -> EXECUTE -> VERIFY
    res1 = skill.execute(world, components)
    assert res1.status == SkillStatus.RUNNING
    print("  ✅ Step 1: BattleSkill executou o ciclo tático mantendo SkillStatus.RUNNING")

    # Step 2: Batalha encerrada -> SUCCESS
    world.battle.in_battle = False
    res2 = skill.execute(world, components)
    assert res2.status == SkillStatus.SUCCESS
    print("  ✅ Step 2: Término de batalha detectado com sucesso (SkillStatus.SUCCESS)")


if __name__ == "__main__":
    test_battle_skill_state_machine_flow()
