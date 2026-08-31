"""
Confidence Updater - Atualização Bayesiana Incremental de Confiança
====================================================================

Atualiza matematicamente o nível de confiança e a maturidade de um LearnedFact
com base nas observações de sucesso e falha confirmadas pelo jogo.

Fórmula de Sucesso:
    confidence += (1.0 - confidence) * 0.25
    - Se sucessos >= 2: status -> LIKELY
    - Se sucessos >= 3 e confidence >= 0.90: status -> CONFIRMED
    - Se sucessos >= 10 e falhas == 0: status -> TRUSTED

Fórmula de Falha:
    confidence *= 0.65
    - Se falhas >= 3 ou confidence < 0.20: status -> REFUTED

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

import time
from .learned_fact import LearnedFact, KnowledgeStatus


class ConfidenceUpdater:
    """
    Atualizador probabilístico de confiança e maturidade do conhecimento.
    """

    @staticmethod
    def success(fact: LearnedFact) -> LearnedFact:
        """Processa um evento de sucesso de teste de hipótese."""
        fact.successes += 1
        fact.observations += 1
        fact.updated_at = time.time()

        # Incremento assintótico em direção a 1.0
        fact.confidence += (1.0 - fact.confidence) * 0.25

        # Transição de Status
        if fact.successes >= 10 and fact.failures == 0 and fact.confidence >= 0.95:
            fact.status = KnowledgeStatus.TRUSTED
        elif fact.successes >= 3 and fact.confidence >= 0.75:
            fact.status = KnowledgeStatus.CONFIRMED
        elif fact.successes >= 2:
            fact.status = KnowledgeStatus.LIKELY

        return fact

    @staticmethod
    def failure(fact: LearnedFact) -> LearnedFact:
        """Processa um evento de falha de teste de hipótese."""
        fact.failures += 1
        fact.observations += 1
        fact.updated_at = time.time()

        # Penalização por falha
        fact.confidence *= 0.65

        # Transição para REFUTED
        if fact.failures >= 3 or fact.confidence < 0.20:
            fact.status = KnowledgeStatus.REFUTED

        return fact
