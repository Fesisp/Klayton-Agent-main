"""
Semantic Observation Data Transfer Objects
===========================================

DTOs imutáveis e estruturados representando a interpretação semântica da cena
fornecida por provedores VLM (Gemini 2.5 Flash, Qwen2.5-VL local, etc.).

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
import time


@dataclass
class SemanticObject:
    """Objeto individual detectado pela percepção semântica."""
    temporary_id: str
    semantic_type: str  # npc, door, stairs, pokemon, chest, signpost, obstacle, item, player
    description: str
    bbox: Optional[Tuple[float, float, float, float]] = None  # (xmin, ymin, xmax, ymax) normalizado [0..1]
    center: Optional[Tuple[float, float]] = None  # (x, y) normalizado [0..1]
    confidence: float = 1.0
    attributes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SemanticRelationship:
    """Relação espacial ou contextual entre dois objetos semânticos."""
    subject_id: str
    relation: str  # behind, near, facing, inside, next_to, blocking
    object_id: str
    confidence: float = 1.0


@dataclass
class PossibleInteraction:
    """Ação de interação plausível sugerida pela percepção semântica."""
    object_index: int
    action: str  # talk, enter, climb, open, inspect, battle, follow
    description: str = ""
    confidence: float = 1.0


@dataclass
class SemanticHypothesis:
    """Hipótese semântica a ser testada e validada no ambiente."""
    hypothesis_id: str
    concept: str
    target_object_id: Optional[str]
    expected_outcome: str  # change_map, open_dialog, heal_team, gain_item, start_battle
    status: str = "HYPOTHESIS"  # HYPOTHESIS, OBSERVED, CONFIRMED, REFUTED
    confidence: float = 1.0
    timestamp: float = field(default_factory=time.time)


@dataclass
class SemanticText:
    """Texto visual presente na cena ou no chat/menu."""
    content: str
    location_box: Optional[Tuple[float, float, float, float]] = None
    language: str = "pt-BR"
    confidence: float = 1.0


@dataclass
class SemanticObservation:
    """Observação semântica unificada da cena capturada."""
    scene_type: Optional[str] = None  # pokemon_center, pokemart, route, cave, gym, event, unknown
    objects: List[SemanticObject] = field(default_factory=list)
    relationships: List[SemanticRelationship] = field(default_factory=list)
    possible_interactions: List[PossibleInteraction] = field(default_factory=list)
    hypotheses: List[SemanticHypothesis] = field(default_factory=list)
    text_elements: List[SemanticText] = field(default_factory=list)
    confidence: float = 1.0
    source: str = "vlm_gemini"  # vlm_gemini, vlm_local, cache, null
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        """Converte a observação em um dicionário serializável em JSON."""
        return {
            "scene_type": self.scene_type,
            "objects": [
                {
                    "temporary_id": obj.temporary_id,
                    "semantic_type": obj.semantic_type,
                    "description": obj.description,
                    "bbox": list(obj.bbox) if obj.bbox else None,
                    "center": list(obj.center) if obj.center else None,
                    "confidence": obj.confidence,
                    "attributes": obj.attributes
                }
                for obj in self.objects
            ],
            "relationships": [
                {
                    "subject_id": rel.subject_id,
                    "relation": rel.relation,
                    "object_id": rel.object_id,
                    "confidence": rel.confidence
                }
                for rel in self.relationships
            ],
            "possible_interactions": [
                {
                    "object_index": inter.object_index,
                    "action": inter.action,
                    "description": inter.description,
                    "confidence": inter.confidence
                }
                for inter in self.possible_interactions
            ],
            "hypotheses": [
                {
                    "hypothesis_id": hyp.hypothesis_id,
                    "concept": hyp.concept,
                    "target_object_id": hyp.target_object_id,
                    "expected_outcome": hyp.expected_outcome,
                    "status": hyp.status,
                    "confidence": hyp.confidence,
                    "timestamp": hyp.timestamp
                }
                for hyp in self.hypotheses
            ],
            "text_elements": [
                {
                    "content": txt.content,
                    "location_box": list(txt.location_box) if txt.location_box else None,
                    "language": txt.language,
                    "confidence": txt.confidence
                }
                for txt in self.text_elements
            ],
            "confidence": self.confidence,
            "source": self.source,
            "timestamp": self.timestamp
        }
