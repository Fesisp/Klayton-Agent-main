"""
Suíte de Testes de GOAP Real & Utility AI - Klayton Companion Agent
===================================================================

Valida:
1. Busca A* no Espaço de Estados do GOAP (Goal -> Plan -> Action Sequence)
2. Interrupção e Retomada de Plano (Push Plan -> Heal -> Pop Plan -> Resume)
3. Decisão Racional da Utility AI (utility = reward - risk - cost - time)

Autor: Klayton Companion Agent Framework
Data: 2026-08-30
"""

import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.world.world_state import WorldState, PokemonInfo
from src.decision.goap_planner import GOAPPlanner
from src.decision.utility_engine import UtilityEngine


def test_goap_a_star_planning():
    print("🧪 Testando GOAP: Planejamento por Busca A* no Espaço de Estados...")
    planner = GOAPPlanner()

    # Estado Inicial: Time ferido, fora da rota de treino, fora de combate
    start_state = {
        "in_battle": False,
        "team_healed": False,
        "needs_heal": True,
        "at_target_map": False,
        "target_level_reached": False
    }

    # Meta do Treinador: Alcançar o nível alvo no Pokémon (ex: Pikachu lvl 35)
    goal_state = {"target_level_reached": True}

    plan = planner.plan(start_state, goal_state)
    action_names = [a.name for a in plan]
    
    assert len(plan) >= 4, f"Plano muito curto: {action_names}"
    assert action_names[0] == "HealTeam"
    assert action_names[1] == "NavigateToFarmArea"
    assert action_names[2] == "HuntInGrass"
    assert action_names[3] == "FightBattle"

    print(f"  ✅ GOAP A* gerou plano perfeito: {' ➔ '.join(action_names)}")


def test_goap_interrupt_and_resume():
    print("\n🧪 Testando GOAP: Interrupção de Treino por HP Crítico e Retomada (Resume)...")
    planner = GOAPPlanner()
    world = WorldState()
    world.team.members.append(PokemonInfo(name="Pikachu", hp_percentage=1.0))

    # 1. Gera plano inicial de treino
    planner.current_plan = planner.plan(
        start_state={"in_battle": False, "team_healed": True, "at_target_map": True, "target_level_reached": False},
        goal_state={"target_level_reached": True}
    )
    initial_actions = [a.name for a in planner.current_plan]
    assert len(planner.current_plan) > 0
    print(f"  ▶️ Plano inicial de treino em execução: {initial_actions}")

    # 2. Simula combate onde HP do Pikachu cai para 15%
    world.team.members[0].hp_percentage = 0.15
    assert world.team.needs_healing is True

    # 3. Interrupção: Salva plano de treino na pilha e gera plano de cura de emergência
    emergency_plan = planner.interrupt_and_push_plan({"team_healed": True}, world)
    assert len(planner.interrupted_plan_stack) == 1
    assert emergency_plan[0].name == "HealTeam"
    print(f"  🚨 Emergência disparada! Plano de treino salvo na pilha. Plano de cura ativo: {[a.name for a in emergency_plan]}")

    # 4. Simula cura concluída
    world.team.members[0].hp_percentage = 1.0
    planner.current_plan = []  # Emergência finalizada

    # 5. Retomada automática (Resume)
    resumed_plan = planner.resume_interrupted_plan(world)
    assert resumed_plan is not None
    assert len(resumed_plan) == len(initial_actions)
    print(f"  ✅ Retomada concluída! O GOAP restaurou o plano de treino: {[a.name for a in resumed_plan]}")


def test_utility_ai_rational_decision():
    print("\n🧪 Testando Utility AI: Decisão Racional em Tempo Real (reward - risk - cost - time)...")
    utility_engine = UtilityEngine()
    world = WorldState()
    candidate_goals = ["HEAL_TEAM", "FOLLOW_FELIPE", "FARM_XP", "EXPLORE"]

    # Cenário A: Time com HP crítico (15%)
    world.team.members.append(PokemonInfo(name="Charizard", hp_percentage=0.15))
    best_goal_a, scores_a = utility_engine.select_best_goal(candidate_goals, world)
    
    print("  📊 Pontuações de Utilidade (Cenário HP Crítico):")
    for g, score in scores_a.items():
        print(f"    - {g:<15}: {score:.1f}")
    assert best_goal_a == "HEAL_TEAM"
    assert scores_a["HEAL_TEAM"] == 92.0
    assert scores_a["FOLLOW_FELIPE"] == 77.0
    assert scores_a["FARM_XP"] == 14.0 or scores_a["FARM_XP"] <= 54.0
    print(f"  ✅ Decisão racional: '{best_goal_a}' escolhido como prioridade máxima!")

    # Cenário B: Time curado (100%)
    world.team.members[0].hp_percentage = 1.0
    best_goal_b, scores_b = utility_engine.select_best_goal(candidate_goals, world)

    print("\n  📊 Pontuações de Utilidade (Cenário Time Curado 100%):")
    for g, score in scores_b.items():
        print(f"    - {g:<15}: {score:.1f}")
    assert best_goal_b in ["FOLLOW_FELIPE", "FARM_XP"]
    assert scores_b["HEAL_TEAM"] == -40.0
    print(f"  ✅ Decisão racional pós-cura: '{best_goal_b}' escolhido autonomamente!")


if __name__ == '__main__':
    print("==========================================================")
    print("🤖 EXECUTANDO TESTES DE GOAP REAL & UTILITY AI")
    print("==========================================================")
    test_goap_a_star_planning()
    test_goap_interrupt_and_resume()
    test_utility_ai_rational_decision()
    print("==========================================================")
    print("🎉 TODOS OS TESTES DE GOAP E UTILITY AI PASSARAM COM 100% DE SUCESSO!")
    print("==========================================================")
