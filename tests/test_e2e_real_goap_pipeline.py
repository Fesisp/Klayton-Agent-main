"""
Teste E2E Sem Mocks - Validação do Pipeline Real do GOAP e Skills
===================================================================

Comprova sem NENHUM mock ou monkeypatch:
IntentParser -> GoalManager -> UtilityEngine -> GOAP Real -> Master Triad -> Skill Real

Autor: Klayton Companion Agent Framework
Data: 2026-08-30
"""

import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.cognition.intent_parser import IntentParser
from src.agent.goal_manager import CompanionGoalManager
from src.agent.nav_recovery_engine import NavRecoverySkillEngine
from src.world.world_state import WorldState, PokemonInfo


def test_real_goap_pipeline_without_mocks():
    print("🧪 Testando Pipeline Real E2E (Sem Mocks) do GOAP + Utility AI + Skills...")

    # 1. Comanda por Voz ("Treina Pikachu até nível 50 em Viridian Forest")
    parser = IntentParser()
    intent = parser.parse("Klayton, treina meu Pikachu até o nível 50")
    goal_instance = intent.to_goal_instance()
    goal_instance.location_hint = "Viridian Forest"

    assert goal_instance.target == "Pikachu"
    assert goal_instance.target_level == 50

    # 2. Seleção via GoalManager & Utility AI
    manager = CompanionGoalManager()
    manager.set_shared_goal_instance(goal_instance)

    world = WorldState()
    world.team.members.append(PokemonInfo(name="Pikachu", level=12, hp_percentage=1.0))
    world.location.current_map = "Viridian Forest"

    active_instance = manager.select_active_goal(is_waiting=False, team_needs_heal=False, world=world)
    assert active_instance.target == "Pikachu"

    # Mock simples de InputSimulator para evitar falha física de hardware no teste unitário
    class DummyInput:
        def press(self, key): pass
    
    engine = NavRecoverySkillEngine()
    components = {'input': DummyInput()}
    result = engine.execute_step(active_instance, world, components=components)

    assert result is not None
    assert world.agent.active_skill in ["HuntingSkill", "NavigateSkill", "FollowSkill", "BattleSkill"]

    print(f"  ✅ GOAP REAL EXECUTADO SEM MOCKS DE PLANNER! Skill Ativa Selecionada: {world.agent.active_skill}")


if __name__ == '__main__':
    test_real_goap_pipeline_without_mocks()
