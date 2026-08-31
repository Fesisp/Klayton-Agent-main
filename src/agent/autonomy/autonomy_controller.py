"""
Autonomy Controller - Controlador Principal de Autonomia de Metas
==================================================================

Orquestra arbitragem de metas, gerenciamento da pilha (GoalStack), decomposição em TaskGraph
e avaliação contínua de progresso empírico.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional
try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger("AutonomyController")

from .goal_candidate import GoalCandidate
from .goal_state import GoalRuntime, GoalState
from .goal_stack import GoalStack
from .goal_arbitrator import GoalArbitrator
from .long_horizon_planner import LongHorizonPlanner
from .task_graph import TaskGraph
from .task_node import TaskNode
from .task_status import TaskStatus
from .goal_progress_evaluator import GoalProgressEvaluator
from .loop_detector import LoopDetector


class AutonomyController:
    """Coordenador central de autonomia de metas do Klayton 2.0."""

    def __init__(self):
        self.stack: GoalStack = GoalStack()
        self.arbitrator: GoalArbitrator = GoalArbitrator()
        self.planner: LongHorizonPlanner = LongHorizonPlanner()
        self.evaluator: GoalProgressEvaluator = GoalProgressEvaluator()
        self.loop_detector: LoopDetector = LoopDetector()

        self.current_task_graph: Optional[TaskGraph] = None

    def tick(self, candidates: List[GoalCandidate], world: Any, components: Dict[str, Any]) -> Optional[GoalRuntime]:
        """Executa um ciclo completo de arbitragem, planejamento e avaliação de progresso."""
        # 1. Arbitragem de Metas
        active_goal = self.arbitrator.select(candidates, self.stack)
        if not active_goal:
            return None

        # 2. Decomposição de Longo Alcance
        if self.current_task_graph is None or active_goal.state == GoalState.PENDING:
            active_goal.state = GoalState.ACTIVE
            active_goal.started_at = active_goal.started_at or time.time()
            self.current_task_graph = self.planner.plan(active_goal, world)
            self.loop_detector.reset()

        # 3. Avaliação de Progresso Empírico no WorldState
        progress_res = self.evaluator.evaluate(world, active_goal)
        active_goal.progress = progress_res.fraction

        # 4. Detecção de Loops Infinitos
        next_task = self.current_task_graph.get_next_ready_task()
        task_id = next_task.id if next_task else "no_task"
        if self.loop_detector.record_step(task_id, progress_res.fraction):
            logger.warning(f"⚠️ AutonomyController: LOOP DETECTADO na tarefa '{task_id}'. Disparando replanejamento...")
            active_goal.replans += 1
            self.current_task_graph = self.planner.plan(active_goal, world)

        # 5. Atualização de Estado da Meta
        if progress_res.complete:
            active_goal.state = GoalState.COMPLETED
            active_goal.completed_at = time.time()
            self.stack.pop()
            self.current_task_graph = None

        return active_goal
