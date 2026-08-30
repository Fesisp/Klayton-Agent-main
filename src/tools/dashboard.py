"""
Agent Dashboard - Painel de Observabilidade CLI em Tempo Real (Fase 22 do Roadmap)
==================================================================================

Exibe o estado operacional completo do Klayton Companion Agent no terminal.

Autor: Klayton Companion Agent Framework
Data: 2026-08-30
"""

import os
import sys
import time
from typing import Any


class AgentDashboard:
    """
    Painel de Observabilidade CLI do Klayton.
    """

    @staticmethod
    def render(agent: Any) -> str:
        """
        Gera uma string formatada contendo o status em tempo real do agente.
        """
        world = agent.world
        goal = agent.goal_manager.shared_goal.name if hasattr(agent, 'goal_manager') else "IDLE"
        skill = world.agent.active_skill or "None"
        map_name = world.location.current_map
        leader = agent.relationship.leader_name if hasattr(agent, 'relationship') else "Player"
        hp_pct = world.team.average_hp_percentage * 100
        pokeballs = world.resources.pokeballs_count
        listening = "SIM" if hasattr(agent, 'voice_listener') and agent.voice_listener.running else "NÃO"

        dashboard_text = f"""
================================================================================
🤖 KLAYTON COMPANION AGENT v2.0 - DASHBOARD DE OBSERVABILIDADE
================================================================================
  📌 Estado Atual      : {world.agent.current_goal}
  🎯 Goal Ativo        : {goal}
  ⚡ Skill em Execução : {skill}
  🗺️ Mapa / Região     : {map_name} ({world.location.region})
  🤝 Líder Acompanhado : {leader} (Instrução: '{getattr(agent.relationship, 'last_instruction', 'Nenhuma')}')
  ❤️ HP Média do Time  : {hp_pct:.1f}% | 🎒 Pokéballs: {pokeballs}
  🎙️ Escuta de Voz     : {listening}
================================================================================
"""
        return dashboard_text
