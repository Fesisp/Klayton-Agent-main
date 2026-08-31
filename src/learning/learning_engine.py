"""
Learning Engine - Coordenador Principal do Autonomous Learning System
=======================================================================

Orquestra a pipeline de aprendizado:
SemanticVision.analyze_unknown ➔ HypothesisEngine.create_test ➔ Executor (SAFE action)
➔ ExperienceValidator.validate ➔ ConfidenceUpdater ➔ KnowledgeBase

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

from typing import Any, List, Optional
from .confidence import ConfidenceUpdater
from .models import LearnedFact, ExplorationRisk
from .hypothesis import HypothesisEngine
from .validator import ExperienceValidator
from .knowledge_base import KnowledgeBase


class LearningEngine:

    def __init__(
        self,
        semantic_vision: Any,
        hypothesis_engine: Optional[HypothesisEngine] = None,
        validator: Optional[ExperienceValidator] = None,
        knowledge_base: Optional[KnowledgeBase] = None,
    ):
        self.semantic_vision = semantic_vision
        self.hypothesis_engine = hypothesis_engine or HypothesisEngine()
        self.validator = validator or ExperienceValidator()
        self.knowledge = knowledge_base or KnowledgeBase()

    async def investigate(
        self,
        frame: Any,
        world: Any,
        executor: Any = None,
        reason: str = "unknown_visual_context",
    ) -> List[LearnedFact]:
        hypotheses = await self.semantic_vision.analyze_unknown(
            frame=frame,
            world_state=world,
            reason=reason,
        )

        results = []

        for fact in hypotheses:
            test = self.hypothesis_engine.create_test(fact)

            if test is None:
                self.knowledge.save_fact(fact)
                continue

            if test.risk != ExplorationRisk.SAFE:
                self.knowledge.save_fact(fact)
                continue

            before = world.snapshot() if hasattr(world, "snapshot") else world

            execution_result = None
            if executor and hasattr(executor, "execute_learning_action"):
                try:
                    execution_result = await executor.execute_learning_action(
                        action=test.action,
                        parameters=test.parameters,
                    )
                except Exception:
                    execution_result = None

            if not execution_result:
                ConfidenceUpdater.failure(fact, 0.5)
                self.knowledge.save_fact(fact)
                results.append(fact)
                continue

            after = world.snapshot() if hasattr(world, "snapshot") else world

            validation = self.validator.validate(
                before=before,
                after=after,
                expectation=test.expected_effect,
            )

            confidence_before = fact.confidence

            if validation.success:
                ConfidenceUpdater.success(
                    fact,
                    validation.confidence,
                )
            else:
                ConfidenceUpdater.failure(
                    fact,
                    validation.confidence,
                )

            self.knowledge.save_fact(fact)
            self.knowledge.save_learning_event(
                concept=fact.concept,
                action=test.action,
                expectation=test.expected_effect,
                success=validation.success,
                confidence_before=confidence_before,
                confidence_after=fact.confidence,
                reason=validation.reason,
            )

            results.append(fact)

        return results

    def get_metrics(self) -> dict:
        """Calcula métricas estatísticas do aprendizado autônomo."""
        facts = self.knowledge.list_facts() if hasattr(self.knowledge, "list_facts") else []
        confirmed = [f for f in facts if str(getattr(f.status, 'value', f.status)).lower() in ["confirmed", "trusted"]]
        refuted = [f for f in facts if str(getattr(f.status, 'value', f.status)).lower() == "refuted"]

        total = len(facts)
        conf_count = len(confirmed)
        ref_count = len(refuted)

        reuse_rate = (conf_count / total) if total > 0 else 0.0
        false_rate = (ref_count / total) if total > 0 else 0.0

        return {
            "total_facts_in_kb": total,
            "confirmed_facts": conf_count,
            "refuted_facts": ref_count,
            "knowledge_reuse_rate": reuse_rate,
            "false_learning_rate": false_rate
        }
