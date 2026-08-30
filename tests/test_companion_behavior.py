"""
Suíte de Testes de Comportamento do Klayton Companion Agent
===========================================================

Testa interrupções de metas, transições de estado por voz e retomada autônoma de objetivos.

Autor: Klayton Companion Agent
Data: 2026-08-30
"""

import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.agent.companion_agent import KlaytonCompanionAgent
from src.world.world_state import PokemonInfo
from src.decision.goal_engine import Goal


def test_low_hp_interrupts_farming():
    print("🧪 Testando: HP baixo interrompe farming e redireciona para cura...")
    agent = KlaytonCompanionAgent()
    agent.goal_manager.shared_goal = Goal.FARM_XP

    # Simula time com HP crítico (15%)
    agent.world.team.members.append(PokemonInfo(name="Charmeleon", hp_percentage=0.15))

    agent.step()

    # O subgoal ativo deve mudar para HEAL_TEAM
    assert agent.world.agent.current_subgoal == "HEAL_TEAM"
    print("  ✅ HP crítico interrompeu o farming e redirecionou o subgoal ativo para HEAL_TEAM!")


def test_voice_wait_interrupts_follow():
    print("🧪 Testando: Comando de voz 'espera aqui' interrompe acompanhamento...")
    agent = KlaytonCompanionAgent()
    agent.goal_manager.shared_goal = Goal.FOLLOW_PLAYER

    agent.listen_and_respond("Klayton, espera aqui por favor")

    assert agent.relationship.is_waiting_for_player is True
    print("  ✅ Comando de voz 'espera aqui' alterou o estado de relacionamento para is_waiting_for_player=True!")


def test_after_heal_agent_resumes_previous_goal():
    print("🧪 Testando: Retomada autônoma de objetivo compartilhado após cura...")
    agent = KlaytonCompanionAgent()
    agent.goal_manager.shared_goal = Goal.FOLLOW_PLAYER

    # 1. Simula time ferido
    agent.world.team.members.append(PokemonInfo(name="Pikachu", hp_percentage=0.10))
    agent.step()
    assert agent.world.agent.current_subgoal == "HEAL_TEAM"

    # 2. Curar time totalmente
    for pkmn in agent.world.team.members:
        pkmn.hp_percentage = 1.0
        pkmn.status = "OK"

    agent.step()

    # Subgoal deve retornar ao objetivo compartilhado principal (FOLLOW_PLAYER)
    assert agent.world.agent.current_subgoal == "FOLLOW_PLAYER"
    print("  ✅ Após a cura, o agente retomou autonomamente o objetivo compartilhado FOLLOW_PLAYER!")


if __name__ == '__main__':
    print("==========================================================")
    print("🤖 EXECUTANDO TESTES DE COMPORTAMENTO DO COMPANION AGENT")
    print("==========================================================")
    test_low_hp_interrupts_farming()
    test_voice_wait_interrupts_follow()
    test_after_heal_agent_resumes_previous_goal()
    print("==========================================================")
    print("🎉 TODOS OS TESTES DE COMPORTAMENTO PASSARAM COM SUCESSO!")
    print("==========================================================")
