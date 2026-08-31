"""
Hypothesis Engine - Motor de Geração e Trava de Segurança de Testes de Hipótese
================================================================================

Responsável por converter hipóteses semânticas em testes concretos executáveis pelo agente,
impondo a Trava de Risco (ExplorationRisk).

Regra de Segurança de Aprendizado Autônomo:
Apenas ações da categoria SAFE (ExplorationRisk.SAFE) são autorizadas para execução e teste autônomo.
Ações com risco MODERATE ou DANGEROUS (comprar/vender, descartar itens, trocar Pokémon) são bloqueadas.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from typing import Dict, Any, Optional
try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger("HypothesisEngine")

from .learned_fact import LearnedFact, ExplorationRisk


class HypothesisEngine:
    """
    Motor que mapeia LearnedFacts para testes com ações e expectativas.
    """

    def create_test(self, fact: LearnedFact) -> Optional[Dict[str, Any]]:
        """
        Cria um teste estruturado para validar a hipótese semântica no jogo.
        Retorna None se a ação for bloqueada pela trava de risco.
        """
        props = fact.properties or {}
        semantic_type = props.get("semantic_type", "unknown").lower()
        interaction = props.get("possible_interaction", "").lower()

        test_plan = None

        if semantic_type in ["door", "stairs", "exit", "portal"]:
            test_plan = {
                "action": "approach_and_cross",
                "expected": "map_changed",
                "risk": ExplorationRisk.SAFE
            }
        elif semantic_type in ["npc", "healer", "shopkeeper", "person"]:
            test_plan = {
                "action": "approach_and_interact",
                "expected": "dialog_opened",
                "risk": ExplorationRisk.SAFE
            }
        elif semantic_type in ["grass", "ground", "path", "water"]:
            test_plan = {
                "action": "walk_over",
                "expected": "movement_success",
                "risk": ExplorationRisk.SAFE
            }
        elif semantic_type in ["chest", "signpost", "item", "object"]:
            test_plan = {
                "action": "inspect_object",
                "expected": "dialog_opened",
                "risk": ExplorationRisk.SAFE
            }
        elif semantic_type in ["pokemon", "wild_target"]:
            test_plan = {
                "action": "approach_and_battle",
                "expected": "battle_started",
                "risk": ExplorationRisk.SAFE
            }
        elif "buy" in interaction or "sell" in interaction or "drop" in interaction or "trade" in interaction:
            # Ações de risco comercial ou de modificação de inventário -> DANGEROUS
            test_plan = {
                "action": "commercial_action",
                "expected": "inventory_changed",
                "risk": ExplorationRisk.DANGEROUS
            }

        if not test_plan:
            return None

        # Trava de Segurança: Apenas ações SAFE são liberadas para exploração autônoma
        if test_plan["risk"].value > ExplorationRisk.SAFE.value:
            logger.warning(f"🛡️ Trava de Risco Ativada: Teste para conceito '{fact.concept}' bloqueado (Risco: {test_plan['risk'].name})")
            return None

        return test_plan
