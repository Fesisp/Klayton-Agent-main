"""
State Guard - Validador de Invariantes de Estado e Decisões Obsoletas
======================================================================

Valida se as decisões do GOAP/Planner continuam válidas examinando o versionamento do WorldState (world.version).

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

from typing import Any, Dict, Optional


class StateGuard:
    """Validador de invariantes e decisões obsoletas."""

    def validate_invariants(self, world: Any, agent_paused: bool) -> bool:
        """Verifica se o estado atual satisfaz as regras invariantes do runtime."""
        if agent_paused:
            # Se o agente estiver pausado, nenhuma ação física deve ser executada
            return True

        if hasattr(world, 'battle') and world.battle.in_battle:
            # Se em batalha, o estado de batalha deve estar marcado como ativo
            if not getattr(world.battle, 'active', True):
                return False

        return True

    def is_decision_stale(self, decision_world_version: int, current_world_version: int, max_allowed_delta: int = 10) -> bool:
        """Retorna True se a decisão foi baseada em uma versão antiga do WorldState."""
        return (current_world_version - decision_world_version) > max_allowed_delta
