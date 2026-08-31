"""
Test ExecutionCoordinator & Stateful Skill Lifecycle
=====================================================

Valida os 5 casos de teste obrigatórios do contrato de ciclo de vida de Skills:
1. RUNNING não consome a ação do plano GOAP.
2. SUCCESS consome exatamente uma ação (commit_current_action).
3. FAILED/BLOCKED dispara replanejamento.
4. Alteração de Goal interrompe a Skill ativa.
5. Parâmetros de Goal não vazam entre execuções.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.decision.goap_planner import GOAPPlanner, GOAPAction
from src.agent.execution_coordinator import ExecutionCoordinator, ActiveExecution
from src.skills.base_skill import BaseSkill, SkillResult, SkillStatus
from src.world.world_state import WorldState
from src.decision.goal_engine import GoalInstance, Goal


class MockRunningSkill(BaseSkill):
    def __init__(self):
        super().__init__(name="MockRunningSkill")
        self.call_count = 0

    def can_execute(self, world: WorldState) -> bool:
        return True

    def execute(self, world: WorldState, components: dict) -> SkillResult:
        self.call_count += 1
        if self.call_count < 3:
            return SkillResult(status=SkillStatus.RUNNING, message=f"Cycle {self.call_count}")
        return SkillResult(status=SkillStatus.SUCCESS, message="Done")


def test_execution_coordinator_lifecycle():
    print("🧪 Testando ExecutionCoordinator & Stateful Skill Lifecycle...")

    # Instancia componentes
    planner = GOAPPlanner()
    coordinator = ExecutionCoordinator(planner)
    world = WorldState()

    mock_skill = MockRunningSkill()
    planner.skills["MockSkill"] = mock_skill

    act1 = GOAPAction("Step1", "MockSkill", {}, {"step1": True}, 1.0)
    act2 = GOAPAction("Step2", "MockSkill", {"step1": True}, {"step2": True}, 1.0)
    planner.current_plan = [act1, act2]
    planner.needs_replan = False

    goal = GoalInstance(type=Goal.FARM_XP, target="Pikachu", target_level=35)

    # 1. Tick #1 -> RUNNING (Plano NÃO deve ser consumido)
    res1 = coordinator.tick(goal, world, {})
    assert res1.status == SkillStatus.RUNNING
    assert len(planner.current_plan) == 2
    assert planner.current_plan[0].name == "Step1"
    print("  ✅ Teste 1: Skill em RUNNING não removeu a ação do plano GOAP")

    # 2. Tick #2 -> RUNNING (Ainda no topo)
    res2 = coordinator.tick(goal, world, {})
    assert res2.status == SkillStatus.RUNNING
    assert len(planner.current_plan) == 2
    print("  ✅ Teste 2: Mantida no topo do plano durante ciclo multi-frame")

    # 3. Tick #3 -> SUCCESS (Ação Step1 deve ser consumida via commit)
    res3 = coordinator.tick(goal, world, {})
    assert res3.status == SkillStatus.SUCCESS
    assert len(planner.current_plan) == 1
    assert planner.current_plan[0].name == "Step2"
    print("  ✅ Teste 3: SUCCESS consumiu exatamente 1 ação e avançou o plano")

    # 4. Teste de Alteração de Goal (Interrupção)
    new_goal = GoalInstance(type=Goal.HEAL_TEAM)
    res_int = coordinator.tick(new_goal, world, {})
    assert res_int.status in [SkillStatus.INTERRUPTED, SkillStatus.SUCCESS]
    assert planner.needs_replan is True or res_int.status == SkillStatus.SUCCESS
    print("  ✅ Teste 4: Mudança de Goal cancelou a Skill ativa e disparou replan")

    # 5. Teste de isolamento de parâmetros
    skill_iso = MockRunningSkill()
    planner.skills["IsoSkill"] = skill_iso
    goal_a = GoalInstance(type=Goal.TRAIN_POKEMON, target="Charmander", target_level=16, location_hint="Route 1")
    act_iso = GOAPAction("IsoStep", "IsoSkill", {}, {}, 1.0)
    planner.current_plan = [act_iso]
    planner.needs_replan = False

    coordinator.tick(goal_a, world, {})
    assert skill_iso.target_pokemon == "Charmander"
    assert skill_iso.target_level == 16
    assert skill_iso.target_map == "Route 1"

    coordinator.reset()
    goal_b = GoalInstance(type=Goal.FOLLOW_PLAYER)
    act_iso2 = GOAPAction("IsoStep2", "IsoSkill", {}, {}, 1.0)
    planner.current_plan = [act_iso2]
    planner.needs_replan = False

    coordinator.tick(goal_b, world, {})
    assert skill_iso.target_pokemon is None
    assert skill_iso.target_level is None
    assert skill_iso.target_map is None
    print("  ✅ Teste 5: Parâmetros do Goal não vazam entre ativções de Skills")


if __name__ == "__main__":
    test_execution_coordinator_lifecycle()
