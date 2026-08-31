"""
Perception Fusion - Fusão Ponderada de Fontes Perceptuais
=========================================================

Realiza a fusão entre a Percepção Rápida (OpenCV, YOLO, OCR, Templates) e a
Percepção Semântica (Gemini / VLM), ponderando a confiança de cada fonte.

Regra da Seção 27 da Especificação:
- Se Fast Perception tem alta confiança (ex: YOLO NPC 95%), Fast Perception prevalece.
- Se Fast Perception está incerta (ex: unknown 35%) e VLM está confiante (ex: Gemini escada 92%), VLM prevalece.
- Nunca usar 'Gemini sempre ganha'. Ponderação estrita por fonte.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from typing import Dict, Any, Optional, List
from .semantic_observation import SemanticObservation
from ..perception_snapshot import PerceptionSnapshot


class PerceptionFusion:
    """
    Fundidor de observações perceptuais com pesos por fonte.
    """

    def __init__(self, fast_weight: float = 1.2, semantic_weight: float = 1.0):
        self.fast_weight = fast_weight
        self.semantic_weight = semantic_weight

    def fuse(
        self,
        base_snapshot: PerceptionSnapshot,
        semantic_obs: Optional[SemanticObservation] = None
    ) -> PerceptionSnapshot:
        """
        Combina o PerceptionSnapshot bruto da percepção rápida com a observação semântica.
        """
        if not semantic_obs or semantic_obs.confidence <= 0.0:
            return base_snapshot

        # 1. Ponderação do Tipo de Cena (Scene Type)
        fast_conf = base_snapshot.confidence * self.fast_weight
        semantic_conf = semantic_obs.confidence * self.semantic_weight

        fused_scene_type = base_snapshot.game_state
        if (base_snapshot.game_state in ["UNKNOWN", "EXPLORING"] or fast_conf < 0.6) and semantic_conf > fast_conf:
            if semantic_obs.scene_type and semantic_obs.scene_type != "unknown":
                fused_scene_type = semantic_obs.scene_type

        # 2. Fusão de Objetos Detectados
        fused_nearby = list(base_snapshot.nearby_players)
        for sem_obj in semantic_obs.objects:
            # Se a confiança semântica for alta, adiciona objeto interpretado
            if sem_obj.confidence >= 0.6:
                fused_nearby.append({
                    "id": sem_obj.temporary_id,
                    "type": sem_obj.semantic_type,
                    "description": sem_obj.description,
                    "center": sem_obj.center,
                    "confidence": sem_obj.confidence,
                    "attributes": sem_obj.attributes
                })

        # 3. Atualiza Snapshot resultante
        base_snapshot.game_state = fused_scene_type
        base_snapshot.nearby_players = fused_nearby
        base_snapshot.confidence = max(base_snapshot.confidence, semantic_obs.confidence)

        return base_snapshot
