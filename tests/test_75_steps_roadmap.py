"""
Suíte de Testes do Roadmap de 75 Etapas - Klayton Companion Agent v1.0
======================================================================

Valida a integridade dos módulos implementados em todas as fases.

Autor: Klayton Companion Agent
Data: 2026-08-30
"""

import sys
import json
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.world.world_state import WorldState, Observation
from src.utils.window_handler import WindowHandler
from src.skills.base_skill import SkillStatus
from src.skills.follow_skill import FollowPlayerSkill
from src.decision.utility_engine import UtilityEngine
from src.agent.companion_agent import KlaytonCompanionAgent


def test_fase1_window_and_observation():
    print("🧪 Testando FASE 1: Isolamento de Janela e Observações com Confiança...")

    win_handler = WindowHandler("PokeOne")
    assert hasattr(win_handler, "is_window_active")
    assert hasattr(win_handler, "activate_window")
    print("  ✅ WindowHandler oferece validação de foco e isolamento de entradas")

    world = WorldState()
    # Observação com confiança baixa (< 0.50) deve ser descartada
    obs_low = Observation(category="battle", data={"in_battle": True}, confidence=0.30)
    applied_low = world.apply_observation(obs_low, min_confidence=0.50)
    assert applied_low is False
    assert world.battle.in_battle is False
    print("  ✅ Observação com confiança < 0.50 descartada com sucesso")

    # Observação com confiança alta (>= 0.50) deve ser aplicada no WorldState
    obs_high = Observation(category="battle", data={"in_battle": True}, confidence=0.95)
    applied_high = world.apply_observation(obs_high, min_confidence=0.50)
    assert applied_high is True
    assert world.battle.in_battle is True
    print("  ✅ Observação com confiança >= 0.50 aplicada no WorldState (Fonte Única da Verdade)")


def test_fase2_skills_and_maps():
    print("\n🧪 Testando FASE 2: Contrato Universal de Skills e Dados de Mapas...")

    skill = FollowPlayerSkill()
    assert hasattr(skill, "can_start")
    assert hasattr(skill, "start")
    assert hasattr(skill, "update")
    assert hasattr(skill, "cancel")
    assert hasattr(skill, "recover")
    assert hasattr(skill, "status")
    assert skill.status() == SkillStatus.READY
    print("  ✅ Contrato Universal da Skill (can_start, start, update, cancel, recover, status) verificado!")

    from src.navigation.map_graph import MapGraph
    graph = MapGraph()
    loaded_count = graph.load_all_maps_from_disk(ROOT_DIR / "data" / "maps")
    assert loaded_count >= 80, f"Esferas de mapas esperadas >= 80, obtido {loaded_count}"
    print(f"  ✅ Base de dados universal de {loaded_count} mapas carregada dinamicamente no MapGraph (Kanto, Johto e Unova)!")

    # Teste de roteamento de grafo global entre Pallet Town e Cerulean City
    route = graph.find_route("Pallet Town", "Cerulean City")
    assert len(route) >= 3, "Falha ao calcular rota global A*"
    print(f"  ✅ Rota global A* calculada com sucesso: {' ➔ '.join(route)}")


def test_fase3_utility_engine():
    print("\n🧪 Testando FASE 3: Utility Engine (reward - risk - cost - time)...")

    utility_engine = UtilityEngine()
    world = WorldState()
    from src.world.world_state import PokemonInfo
    world.team.members.append(PokemonInfo(name="Pikachu", hp_percentage=0.15))

    scores = utility_engine.evaluate_goals(["HEAL_TEAM", "FOLLOW_PLAYER", "EXPLORE"], world)
    assert scores["HEAL_TEAM"] > scores["FOLLOW_PLAYER"]
    print(f"  ✅ Utility AI pontuou prioridade máxima para cura: HEAL_TEAM ({scores['HEAL_TEAM']:.1f}) > FOLLOW_PLAYER ({scores['FOLLOW_PLAYER']:.1f})")


def test_companion_agent_step():
    print("\n🧪 Testando Execução do Loop do KlaytonCompanionAgent...")

    agent = KlaytonCompanionAgent()
    agent.step()
    assert agent.world.agent.is_running is True
    print("  ✅ KlaytonCompanionAgent executou ciclo do runtime com sucesso!")


if __name__ == '__main__':
    print("==========================================================")
    print("🤖 EXECUTANDO TESTES DAS FASES DO ROADMAP V1.0")
    print("==========================================================")
    test_fase1_window_and_observation()
    test_fase2_skills_and_maps()
    test_fase3_utility_engine()
    test_companion_agent_step()
    print("==========================================================")
    print("🎉 TODOS OS TESTES DO ROADMAP PASSARAM COM 100% DE SUCESSO!")
    print("==========================================================")
