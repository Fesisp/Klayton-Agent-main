"""
Target Tracker - Rastreamento Persistente de Alvos em Coordenadas Egocêntricas
==============================================================================

Sistema de rastreamento com sistema de coordenadas centrado no personagem Klayton (0.5, 0.5).
Gerencia oclusões temporárias, predição de movimento por velocidade e re-identificação de alvos.

Occlusion Management Pipeline:
- 0–500ms: predição contínua pelo tracker
- 500ms–2.0s: estimativa por velocidade e busca local
- > 2.0s: fallback para detector global / VLM
- > 5.0s: marca o alvo como perdido (target_lost)

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger("TargetTracker")


PLAYER_SCREEN_POSITION: Tuple[float, float] = (0.5, 0.5)


@dataclass
class TrackedEntity:
    """Entidade individual rastreada no campo visual."""
    entity_id: str
    semantic_type: str
    description: str
    bbox: Optional[Tuple[float, float, float, float]] = None  # (ymin, xmin, ymax, xmax)
    center: Tuple[float, float] = (0.5, 0.5)  # (x_norm, y_norm)
    velocity: Tuple[float, float] = (0.0, 0.0)  # (vx, vy) por segundo
    last_seen: float = field(default_factory=time.time)
    confidence: float = 1.0
    identity_features: Dict[str, Any] = field(default_factory=dict)
    is_occluded: bool = False

    @property
    def age(self) -> float:
        return time.time() - self.last_seen


class TargetTracker:
    """
    Rastreador egocêntrico de entidades com tolerância a oclusões.
    """

    def __init__(self, occluded_timeout: float = 5.0):
        self.tracked_entities: Dict[str, TrackedEntity] = {}
        self.occluded_timeout = occluded_timeout

    def update_from_observation(self, detected_objects: List[Any]) -> None:
        """
        Atualiza o estado dos alvos rastreados com novas observações visuais.
        """
        now = time.time()
        seen_ids = set()

        for obj in detected_objects:
            obj_id = getattr(obj, 'temporary_id', None) or getattr(obj, 'semantic_type', 'obj')
            center = getattr(obj, 'center', None) or (0.5, 0.5)
            bbox = getattr(obj, 'bbox', None)
            desc = getattr(obj, 'description', '')
            stype = getattr(obj, 'semantic_type', 'unknown')

            if obj_id in self.tracked_entities:
                entity = self.tracked_entities[obj_id]
                # Calcula velocidade de deslocamento relativa ao frame anterior
                dt = max(0.001, now - entity.last_seen)
                vx = (center[0] - entity.center[0]) / dt
                vy = (center[1] - entity.center[1]) / dt

                entity.center = center
                entity.bbox = bbox
                entity.velocity = (vx, vy)
                entity.last_seen = now
                entity.is_occluded = False
                entity.confidence = getattr(obj, 'confidence', 0.9)
            else:
                self.tracked_entities[obj_id] = TrackedEntity(
                    entity_id=obj_id,
                    semantic_type=stype,
                    description=desc,
                    bbox=bbox,
                    center=center,
                    last_seen=now,
                    confidence=getattr(obj, 'confidence', 0.9)
                )
            seen_ids.add(obj_id)

        # Trata oclusão para entidades que não foram vistas no frame atual
        for entity_id, entity in list(self.tracked_entities.items()):
            if entity_id not in seen_ids:
                dt = now - entity.last_seen
                entity.is_occluded = True

                if dt <= 0.5:
                    # 0-500ms: Predição contínua
                    pred_x = entity.center[0] + entity.velocity[0] * dt
                    pred_y = entity.center[1] + entity.velocity[1] * dt
                    entity.center = (max(0.0, min(1.0, pred_x)), max(0.0, min(1.0, pred_y)))
                elif dt > self.occluded_timeout:
                    # > 5s: Alvo perdido
                    logger.debug(f"🎯 Alvo '{entity_id}' perdido por oclusão prolongada ({dt:.1f}s)")
                    del self.tracked_entities[entity_id]

    def get_tracked_target(self, target_id: str) -> Optional[TrackedEntity]:
        """Retorna uma entidade rastreada pelo seu ID."""
        return self.tracked_entities.get(target_id)
