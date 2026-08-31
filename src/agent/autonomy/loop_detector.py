"""
Loop Detector - Detecção de Ciclos Infinitos Sem Progresso
==========================================================

Rastreia repetições idênticas de tarefas sem alteração de progresso para evitar loops infinitos.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

from typing import List, Tuple


class LoopDetector:
    """Detector de loops repetitivos em planejamento de metas."""

    def __init__(self, loop_threshold: int = 4):
        self.loop_threshold = loop_threshold
        self.history: List[Tuple[str, float]] = []

    def record_step(self, task_id: str, progress_fraction: float) -> bool:
        """
        Registra uma etapa. Retorna True se um loop infinito for detectado.
        """
        item = (task_id, round(progress_fraction, 3))
        self.history.append(item)

        if len(self.history) >= self.loop_threshold:
            recent = self.history[-self.loop_threshold:]
            if len(set(recent)) == 1:
                return True

        return False

    def reset(self) -> None:
        self.history.clear()
