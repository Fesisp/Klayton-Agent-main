"""
Confidence Updater - Algoritmo de Atualização Probabilística de Confiança
==========================================================================

Atualiza matematicamente o nível de confiança e o status de maturidade (KnowledgeStatus)
de um LearnedFact ponderado pela força da evidência (evidence_strength).

Fórmulas:
- Sucesso: confidence += (1.0 - confidence) * (0.20 * evidence_strength)
- Falha:   confidence *= (1.0 - 0.35 * evidence_strength)

Maturidade:
- LIKELY: successes >= 2
- CONFIRMED: successes >= 3 e confidence >= 0.90
- TRUSTED: successes >= 10 e confidence >= 0.97
- REFUTED: failures >= 3 ou confidence <= 0.20

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

import time
from .models import LearnedFact, KnowledgeStatus


class ConfidenceUpdater:

    @staticmethod
    def success(
        fact: LearnedFact,
        evidence_strength: float = 1.0,
    ) -> LearnedFact:

        fact.successes += 1
        fact.observations += 1
        fact.last_seen = time.time()

        gain = 0.20 * max(0.0, min(evidence_strength, 1.0))
        fact.confidence += (1.0 - fact.confidence) * gain

        if fact.successes >= 10 and fact.confidence >= 0.95:
            fact.status = KnowledgeStatus.TRUSTED
        elif fact.successes >= 3 and fact.confidence >= 0.70:
            fact.status = KnowledgeStatus.CONFIRMED
        elif fact.successes >= 2:
            fact.status = KnowledgeStatus.LIKELY

        return fact

    @staticmethod
    def failure(
        fact: LearnedFact,
        evidence_strength: float = 1.0,
    ) -> LearnedFact:

        fact.failures += 1
        fact.observations += 1
        fact.last_seen = time.time()

        penalty = 0.35 * max(0.0, min(evidence_strength, 1.0))
        fact.confidence *= (1.0 - penalty)

        if fact.failures >= 3 or fact.confidence <= 0.20:
            fact.status = KnowledgeStatus.REFUTED

        return fact
