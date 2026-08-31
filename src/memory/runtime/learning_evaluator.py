"""
Learning Evaluator - Avaliador de Aprendizado
=============================================

Avalia eventos de combate, navegação e metas para extrair aprendizados empíricos.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

from typing import Any, Dict
from .memory_record import MemoryRecord
from .memory_type import MemoryType
from .provenance import EvidenceSource


class LearningEvaluator:
    """Avaliador de eventos para extração de aprendizado."""

    def evaluate_battle_outcome(self, battle_data: Dict[str, Any]) -> MemoryRecord:
        key = f"battle_strategy_{battle_data.get('enemy_name', 'unknown')}"
        val = {
            "action": battle_data.get("action"),
            "success": battle_data.get("success", False),
            "delta_hp": battle_data.get("delta_hp", 0.0)
        }
        return MemoryRecord(
            type=MemoryType.EPISODIC,
            key=key,
            value=val,
            confidence=0.90 if battle_data.get("success") else 0.60,
            source=EvidenceSource.DIRECT_OBSERVATION,
            tags={"battle", "outcome"}
        )

    def evaluate_navigation_outcome(self, nav_data: Dict[str, Any]) -> MemoryRecord:
        key = f"route_reliability_{nav_data.get('source')}_to_{nav_data.get('target')}"
        val = {
            "success": nav_data.get("success", False),
            "duration": nav_data.get("duration", 0.0)
        }
        return MemoryRecord(
            type=MemoryType.EPISODIC,
            key=key,
            value=val,
            confidence=0.95 if nav_data.get("success") else 0.50,
            source=EvidenceSource.DIRECT_OBSERVATION,
            tags={"navigation", "route"}
        )
