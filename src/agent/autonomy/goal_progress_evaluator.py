"""
Goal Progress Evaluator - Avaliador Empírico de Avanço de Meta
==============================================================

Mede o progresso real e a conclusão de uma meta através das mudanças observáveis no WorldState.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

from typing import Any
from .goal_state import GoalRuntime, GoalState
from .goal_progress import GoalProgress


class GoalProgressEvaluator:
    """Avaliador empírico de progresso de metas com base no WorldState."""

    def evaluate(self, world: Any, goal: GoalRuntime) -> GoalProgress:
        """Mede o progresso real a partir do WorldState."""
        if not goal or not goal.candidate:
            return GoalProgress(fraction=0.0, advanced=False, blocked=False, complete=False, reason="Meta inválida")

        gt = goal.candidate.goal_type.upper()

        # 1. Metas de Treinamento (Ex: TRAIN_POKEMON)
        if "TRAIN" in gt or "FARM" in gt:
            target_level = goal.candidate.target_level or 35
            target_pkmn_name = goal.candidate.target or "Pikachu"

            curr_level = 1
            if hasattr(world, 'team') and world.team.members:
                for pkmn in world.team.members:
                    if pkmn.name.lower() == target_pkmn_name.lower() and pkmn.level is not None:
                        curr_level = pkmn.level
                        break

            initial_level = goal.metadata.get("initial_level", curr_level)
            if "initial_level" not in goal.metadata:
                goal.metadata["initial_level"] = curr_level

            if curr_level >= target_level:
                return GoalProgress(fraction=1.0, advanced=True, blocked=False, complete=True, reason=f"{target_pkmn_name} atingiu o nível {curr_level}")

            range_tot = max(1, target_level - initial_level)
            gained = max(0, curr_level - initial_level)
            frac = min(0.99, gained / range_tot)

            advanced = curr_level > goal.metadata.get("last_seen_level", initial_level)
            goal.metadata["last_seen_level"] = curr_level

            return GoalProgress(fraction=frac, advanced=advanced, blocked=False, complete=False, reason=f"Nível atual: {curr_level}/{target_level}")

        # 2. Metas de Navegação (Ex: NAVIGATE)
        elif "NAVIGATE" in gt or "GO" in gt or "RETURN" in gt:
            target_map = goal.candidate.location_hint or goal.candidate.target
            curr_map = getattr(world.location, 'current_map', 'Unknown')

            if target_map and curr_map.lower() == target_map.lower():
                return GoalProgress(fraction=1.0, advanced=True, blocked=False, complete=True, reason=f"Chegamos a {target_map}")

            return GoalProgress(fraction=0.5, advanced=True, blocked=False, complete=False, reason=f"Em trânsito de {curr_map} para {target_map}")

        # 3. Metas de Cura (Ex: HEAL_TEAM)
        elif "HEAL" in gt:
            needs_heal = getattr(world.team, 'needs_healing', False) if hasattr(world, 'team') else False
            if not needs_heal:
                return GoalProgress(fraction=1.0, advanced=True, blocked=False, complete=True, reason="Time totalmente curado")
            return GoalProgress(fraction=0.3, advanced=False, blocked=False, complete=False, reason="Time necessita de cura")

        return GoalProgress(fraction=0.5, advanced=False, blocked=False, complete=False, reason="Em andamento")
