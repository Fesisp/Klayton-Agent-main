"""
Human Feedback & Decision Quality Tracking
===========================================

Permite a supervisão humana simplificada (correto / incorreto) sem rotulagem manual exaustiva,
e registra logs de acompanhamento de qualidade de decisão (Knowledge Accuracy vs Decision Quality).

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

import time
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from .learned_fact import LearnedFact, KnowledgeStatus


@dataclass
class DecisionRecord:
    """Registro de qualidade de decisão para comparação entre o previso e o observado."""
    goal: str
    selected_action: str
    predicted_reward: float
    predicted_risk: float
    actual_reward: Optional[float] = None
    success: Optional[bool] = None
    duration: Optional[float] = None
    timestamp: float = field(default_factory=time.time)


class HumanFeedbackSystem:
    """
    Sistema de supervisão humana por validação direta de acontecimentos relevantes.
    """

    @staticmethod
    def apply_feedback(fact: LearnedFact, feedback: str) -> LearnedFact:
        """
        Aplica o feedback do supervisor humano:
        - "correct" / "sim": Promove imediatamente a confiança >= 0.95 e status CONFIRMED
        - "incorrect" / "nao": Refuta imediatamente o fato (confidence = 0.0, status REFUTED)
        """
        clean_fb = feedback.lower().strip()
        now = time.time()
        fact.updated_at = now

        if clean_fb in ["correct", "sim", "yes", "certo"]:
            fact.confidence = max(fact.confidence, 0.95)
            fact.status = KnowledgeStatus.CONFIRMED
            fact.successes += 1
            fact.observations += 1
        elif clean_fb in ["incorrect", "nao", "no", "errado"]:
            fact.confidence = 0.0
            fact.status = KnowledgeStatus.REFUTED
            fact.failures += 1
            fact.observations += 1

        return fact
