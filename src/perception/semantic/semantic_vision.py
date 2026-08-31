"""
Semantic Vision - Interface de Percepção Semântica para Geração de Hipóteses
============================================================================

Conecta o motor de VLM (Gemini / Null provider) ao subsistema de Aprendizado,
convertendo a resposta multimodal em instâncias do modelo LearnedFact.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

from typing import Any, List, Dict
from ...learning.models import LearnedFact


class SemanticVision:
    """
    Interface de visão semântica para análise de elementos desconhecidos no jogo.
    """

    def __init__(self, provider: Any):
        self.provider = provider

    async def analyze_unknown(
        self,
        frame: Any,
        world_state: Any,
        reason: str = "unknown_visual_context",
    ) -> List[LearnedFact]:
        """
        Solicita a análise do VLM para uma cena com elementos desconhecidos
        e converte os objetos detectados em hipóteses (LearnedFact).
        """
        if frame is None:
            return []

        agent_obj = getattr(world_state, "agent", None) if world_state else None
        game_state = getattr(agent_obj, "current_state", None) or getattr(agent_obj, "current_goal", "UNKNOWN")
        current_goal = getattr(agent_obj, "current_goal", None) or "EXPLORE"

        request = {
            "reason": reason,
            "game_state": game_state,
            "current_goal": current_goal,
            "instructions": [
                "Describe only visually supported facts.",
                "Return uncertainty explicitly.",
                "Identify objects relevant to navigation or interaction.",
                "Do not treat guesses as facts.",
            ],
        }

        try:
            response = await self.provider.analyze(
                image=frame,
                request=request,
            )
            return self._to_hypotheses(response or {})
        except Exception:
            return []

    def _to_hypotheses(self, response: Dict[str, Any]) -> List[LearnedFact]:
        facts: List[LearnedFact] = []

        for obj in response.get("objects", []):
            semantic_type = obj.get("type", "unknown")
            confidence = float(obj.get("confidence", 0.50))

            facts.append(
                LearnedFact(
                    concept=f"visual:{semantic_type}",
                    properties={
                        "semantic_type": semantic_type,
                        "description": obj.get("description"),
                        "position": obj.get("position"),
                        "bbox": obj.get("bbox"),
                        "possible_interaction": obj.get(
                            "possible_interaction"
                        ),
                    },
                    confidence=max(0.0, min(confidence, 1.0)),
                    source="semantic_ai",
                )
            )

        return facts
