"""
Teste End-to-End da Transmissão de Parâmetros (GoalInstance Pipeline)
======================================================================

Comprova sem inferências que comandos como "Treina Pikachu até nível 50":
1. Geram GoalInstance com target="Pikachu" e target_level=50.
2. Ativam a meta pessoal no CompanionGoalManager.
3. Transmitem target_level=50 até a Skill ativa em NavRecoverySkillEngine.

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
from src.world.world_state import WorldState
from src.skills.hunting_skill import HuntingSkill


def test_e2e_goal_instance_parameter_transmission():
    print("🧪 Testando Transmissão End-to-End de Parâmetros (GoalInstance ➔ Skill)...")

    # 1. Parsing de Linguagem Natural
    parser = IntentParser()
    intent = parser.parse("Klayton, treina meu Pikachu até o nível 50")
    assert intent.target == "Pikachu"
    assert intent.constraints.get("target_level") == 50

    # 2. Geração da GoalInstance
    goal_instance = intent.to_goal_instance()
    assert goal_instance.target == "Pikachu"
    assert goal_instance.target_level == 50

    # 3. Gerenciamento e Seleção de Metas
    manager = CompanionGoalManager()
    manager.set_shared_goal_instance(goal_instance)

    selected_instance = manager.select_active_goal(is_waiting=False, team_needs_heal=False)
    assert selected_instance.target == "Pikachu"
    assert selected_instance.target_level == 50

    # 4. Injeção de Parâmetros na Skill via NavRecoverySkillEngine
    engine = NavRecoverySkillEngine()
    world = WorldState()

    # Cria uma Skill de teste para receber a injeção
    test_skill = HuntingSkill()
    test_skill.target_level = 35  # Valor padrão antigo

    from src.decision.goap_planner import GOAPAction
    engine.goap_planner.peek_next_action = lambda goal, w: (GOAPAction("HuntEncounter", "HuntingSkill", {}, {}, 1.0), test_skill)
    engine.goap_planner.skills["HuntingSkill"] = test_skill

    # Executa o step com a GoalInstance parametrizada
    engine.execute_step(selected_instance, world, components={})

    # Assevera que o parâmetro target_level=50 alterou dinamicamente a Skill!
    assert test_skill.target_level == 50
    assert test_skill.target_pokemon == "Pikachu"

    print(f"  ✅ Parâmetro transmitido com 100% de sucesso! Skill.target_level = {test_skill.target_level} | Skill.target_pokemon = '{test_skill.target_pokemon}'")


if __name__ == '__main__':
    test_e2e_goal_instance_parameter_transmission()
