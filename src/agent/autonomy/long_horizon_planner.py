"""
Long Horizon Planner - Planejador de Alto Nível de Longo Alcance
================================================================

Decompõe metas complexas em um grafo de tarefas encadeadas (TaskGraph).

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

from typing import Any, Optional
from .goal_state import GoalRuntime
from .task_graph import TaskGraph
from .task_node import TaskNode
from .task_status import TaskStatus


class LongHorizonPlanner:
    """Planejador de decomposição de metas complexas em grafos de tarefas."""

    def plan(self, goal: GoalRuntime, world: Any = None) -> TaskGraph:
        """Constrói o TaskGraph para a meta fornecida."""
        graph = TaskGraph()

        if not goal or not goal.candidate:
            return graph

        gt = goal.candidate.goal_type.upper()

        # Decomposição para Treinamento de Pokémon
        if "TRAIN" in gt or "FARM" in gt:
            t1 = TaskNode(id="t1_check_team", task_type="CHECK_TEAM_READY")
            t2 = TaskNode(id="t2_reach_area", task_type="NAVIGATE_TO_AREA", dependencies=["t1_check_team"])
            t3 = TaskNode(id="t3_farm_xp", task_type="FARM_XP", dependencies=["t2_reach_area"])
            t4 = TaskNode(id="t4_verify_level", task_type="VERIFY_TARGET_LEVEL", dependencies=["t3_farm_xp"])

            graph.add_task(t1)
            graph.add_task(t2)
            graph.add_task(t3)
            graph.add_task(t4)

        # Decomposição para Compra de Item
        elif "BUY" in gt or "SHOP" in gt:
            t1 = TaskNode(id="t1_find_shop", task_type="NAVIGATE_TO_SHOP")
            t2 = TaskNode(id="t2_buy_items", task_type="INTERACT_AND_BUY", dependencies=["t1_find_shop"])

            graph.add_task(t1)
            graph.add_task(t2)

        else:
            t1 = TaskNode(id="t1_generic_execute", task_type="EXECUTE_GOAL")
            graph.add_task(t1)

        return graph
