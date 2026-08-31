"""
Hypothesis Engine - Gerador de Testes de Hipótese
=================================================

Converte hipóteses semânticas em testes de aprendizado seguros (LearningTest)
com ação pretendida, efeito esperado e nível de risco.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

from typing import Optional
from .models import LearnedFact, LearningTest, ExplorationRisk


class HypothesisEngine:

    def create_test(self, fact: LearnedFact) -> Optional[LearningTest]:
        semantic_type = fact.properties.get("semantic_type")
        interaction = fact.properties.get("possible_interaction")

        if semantic_type == "door":
            return LearningTest(
                action="approach_and_cross",
                expected_effect="map_changed",
                risk=ExplorationRisk.SAFE,
                parameters={"target": fact.properties},
            )

        if semantic_type in {"npc", "character"}:
            return LearningTest(
                action="approach_and_interact",
                expected_effect="dialog_opened",
                risk=ExplorationRisk.SAFE,
                parameters={"target": fact.properties},
            )

        if semantic_type in {"grass", "floor", "path"}:
            return LearningTest(
                action="walk_over",
                expected_effect="movement_success",
                risk=ExplorationRisk.SAFE,
                parameters={"target": fact.properties},
            )

        if interaction == "talk":
            return LearningTest(
                action="approach_and_interact",
                expected_effect="dialog_opened",
                risk=ExplorationRisk.SAFE,
                parameters={"target": fact.properties},
            )

        return None
