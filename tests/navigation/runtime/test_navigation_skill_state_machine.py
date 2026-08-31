"""
Test NavigateSkill State Machine - Ciclo Fechado e Interrupção por Batalha
===========================================================================

Valida:
1. Execução da NavigateSkill mantendo SkillStatus.RUNNING.
2. Pausa temporária em combate sem destruir a rota ativa.
3. Retorno de SkillStatus.SUCCESS somente ao confirmar chegada ao destino.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.skills.navigate_skill import NavigateSkill
from src.skills.base_skill import SkillStatus
from src.world.world_state import WorldState


class MockInputSimulator:
    def press(self, key: str):
        pass


def test_navigate_skill_state_machine_flow():
    print("🧪 Testando NavigateSkill State Machine (Ciclo Fechado & Interrupções)...")

    skill = NavigateSkill(target_map="Viridian City")
    world = WorldState()
    world.location.current_map = "Pallet Town"
    components = {"input": MockInputSimulator()}

    # Step 1: Início de navegação -> RUNNING
    res1 = skill.execute(world, components)
    assert res1.status == SkillStatus.RUNNING
    print("  ✅ Step 1: NavigateSkill iniciou o deslocamento em estado RUNNING")

    # Step 2: Batalha surge -> Pausa temporária sem quebrar a rota
    world.battle.in_battle = True
    res2 = skill.execute(world, components)
    assert res2.status == SkillStatus.RUNNING
    assert "pausada temporariamente" in res2.message
    print("  ✅ Step 2: Batalha pausou temporariamente a navegação sem destruir o progresso")

    # Step 3: Batalha termina e chega ao destino -> SUCCESS
    world.battle.in_battle = False
    world.location.current_map = "Viridian City"
    res3 = skill.execute(world, components)
    assert res3.status == SkillStatus.SUCCESS
    print("  ✅ Step 3: Chegada ao mapa destino 'Viridian City' confirmou SkillStatus.SUCCESS")


if __name__ == "__main__":
    test_navigate_skill_state_machine_flow()
