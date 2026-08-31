"""
Gemini Vision Provider - Integração com Gemini 2.5 Flash
=========================================================

Implementa o provedor de visão semântica utilizando o modelo Gemini 2.5 Flash
da Google via SDK oficial (google-genai) ou HTTP REST fallback com resposta estruturada em JSON.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

import os
import io
import json
import base64
from typing import Dict, Any, Optional, List
try:
    from PIL import Image
except ImportError:
    Image = None

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger("GeminiVisionProvider")

from .base_provider import VisionLanguageProvider
from ..semantic_observation import (
    SemanticObservation, SemanticObject, SemanticRelationship,
    PossibleInteraction, SemanticHypothesis, SemanticText
)

# Tenta importar google.genai ou google.generativeai se instalado
GENAI_AVAILABLE = False
try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    try:
        import google.generativeai as genai_legacy
        GENAI_AVAILABLE = True
    except ImportError:
        GENAI_AVAILABLE = False


SYSTEM_PROMPT = """Você é o módulo de percepção semântica de um agente autônomo chamado Klayton.
O agente está jogando o MMO PokeOne.

Estado conhecido do agente:
- O personagem controlado permanece no centro da tela (coordenadas egocêntricas [0.5, 0.5]).
- Analise apenas informações visuais verificáveis na imagem.

Sua tarefa é analisar a imagem e retornar EXCLUSIVAMENTE um objeto JSON estruturado com os seguintes campos:
{
  "scene_type": "pokemon_center" | "pokemart" | "route" | "cave" | "gym" | "event" | "unknown",
  "objects": [
    {
      "temporary_id": "obj_1",
      "semantic_type": "npc" | "door" | "stairs" | "pokemon" | "chest" | "signpost" | "obstacle" | "item" | "player",
      "description": "descrição concisa em português",
      "bbox": [ymin, xmin, ymax, xmax],
      "center": [x_norm, y_norm],
      "confidence": 0.9,
      "attributes": {}
    }
  ],
  "relationships": [
    {
      "subject_id": "obj_1",
      "relation": "behind" | "near" | "facing" | "inside" | "next_to" | "blocking",
      "object_id": "obj_2",
      "confidence": 0.85
    }
  ],
  "possible_interactions": [
    {
      "object_index": 0,
      "action": "talk" | "enter" | "climb" | "open" | "inspect" | "battle" | "follow",
      "description": "falar com o NPC healler",
      "confidence": 0.9
    }
  ],
  "hypotheses": [
    {
      "hypothesis_id": "hyp_1",
      "concept": "stairs",
      "target_object_id": "obj_1",
      "expected_outcome": "change_map",
      "status": "HYPOTHESIS",
      "confidence": 0.85
    }
  ],
  "text_elements": [
    {
      "content": "texto lido na tela",
      "location_box": [ymin, xmin, ymax, xmax],
      "language": "pt-BR",
      "confidence": 0.95
    }
  ],
  "confidence": 0.9
}
Retorne estritamente o JSON sem marcações de código markdown extras se possível ou formato markdown json limpo.
"""


class GeminiVisionProvider(VisionLanguageProvider):
    """
    Provedor de inteligência visual semântica baseado no Gemini 2.5 Flash.
    """

    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-2.5-flash", config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.model_name = self.config.get("semantic_ai", {}).get("model", model_name)
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or self.config.get("semantic_ai", {}).get("api_key")
        self.client = None

        if self.api_key and GENAI_AVAILABLE:
            try:
                if 'genai' in globals() and hasattr(genai, 'Client'):
                    self.client = genai.Client(api_key=self.api_key)
                elif 'genai_legacy' in globals():
                    genai_legacy.configure(api_key=self.api_key)
                    self.client = genai_legacy.GenerativeModel(self.model_name)
            except Exception as e:
                logger.warning(f"⚠️ Não foi possível inicializar cliente Gemini: {e}")

    def _prepare_image_bytes(self, image: Any) -> Optional[bytes]:
        """Converte diferentes formatos de imagem (numpy array, PIL Image, bytes) para JPEG bytes."""
        if image is None:
            return None
        if isinstance(image, bytes):
            return image

        # PIL Image
        if Image and isinstance(image, Image.Image):
            buf = io.BytesIO()
            image.save(buf, format="JPEG")
            return buf.getvalue()

        # Numpy ndarray (OpenCV BGR or RGB)
        try:
            import numpy as np
            if isinstance(image, np.ndarray):
                import cv2
                # Se for 3 canais BGR, converte para RGB se necessário
                if len(image.shape) == 3 and image.shape[2] == 3:
                    rgb_img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                else:
                    rgb_img = image
                pil_img = Image.fromarray(rgb_img)
                buf = io.BytesIO()
                pil_img.save(buf, format="JPEG")
                return buf.getvalue()
        except Exception:
            pass

        return None

    async def analyze(self, image: Any, request: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Envia a imagem para o Gemini 2.5 Flash e decodifica a resposta estruturada em dicionário.
        """
        img_bytes = self._prepare_image_bytes(image)
        if not img_bytes or not self.api_key:
            return {"scene_type": "unknown", "objects": []}

        request_context = request or {}
        context_str = f"\nContexto do Agente: {json.dumps(request_context, ensure_ascii=False)}"
        prompt = SYSTEM_PROMPT + context_str

        try:
            raw_response_text = ""
            if self.client and hasattr(self.client, 'models'):
                img_part = types.Part.from_bytes(data=img_bytes, mime_type="image/jpeg")
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=[prompt, img_part],
                )
                raw_response_text = response.text
            else:
                import requests
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"
                b64_img = base64.b64encode(img_bytes).decode('utf-8')
                payload = {
                    "contents": [{
                        "parts": [
                            {"text": prompt},
                            {
                                "inline_data": {
                                    "mime_type": "image/jpeg",
                                    "data": b64_img
                                }
                            }
                        ]
                    }],
                    "generationConfig": {
                        "response_mime_type": "application/json"
                    }
                }
                res = requests.post(url, json=payload, timeout=10.0)
                if res.status_code == 200:
                    res_json = res.json()
                    candidates = res_json.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts:
                            raw_response_text = parts[0].get("text", "")

            if not raw_response_text:
                return {"scene_type": "unknown", "objects": []}

            cleaned = raw_response_text.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()

            return json.loads(cleaned)

        except Exception as e:
            logger.warning(f"⚠️ Erro ao consultar Gemini 2.5 Flash: {e}")
            return {"scene_type": "unknown", "objects": []}

    def _parse_json_response(self, text: str) -> SemanticObservation:
        """Decodifica a resposta JSON e popula a classe SemanticObservation."""
        cleaned = text.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        try:
            data = json.loads(cleaned)
        except Exception:
            logger.debug(f"Não foi possível parsear JSON do Gemini: {text}")
            return SemanticObservation(scene_type="unknown", confidence=0.1, source="gemini_parse_error")

        objects = []
        for obj in data.get("objects", []):
            bbox = tuple(obj["bbox"]) if obj.get("bbox") and len(obj["bbox"]) == 4 else None
            center = tuple(obj["center"]) if obj.get("center") and len(obj["center"]) == 2 else None
            objects.append(SemanticObject(
                temporary_id=obj.get("temporary_id", "obj_x"),
                semantic_type=obj.get("semantic_type", "unknown"),
                description=obj.get("description", ""),
                bbox=bbox,
                center=center,
                confidence=float(obj.get("confidence", 0.9)),
                attributes=obj.get("attributes", {})
            ))

        relationships = []
        for rel in data.get("relationships", []):
            relationships.append(SemanticRelationship(
                subject_id=rel.get("subject_id", ""),
                relation=rel.get("relation", "near"),
                object_id=rel.get("object_id", ""),
                confidence=float(rel.get("confidence", 0.85))
            ))

        interactions = []
        for inter in data.get("possible_interactions", []):
            interactions.append(PossibleInteraction(
                object_index=int(inter.get("object_index", 0)),
                action=inter.get("action", "inspect"),
                description=inter.get("description", ""),
                confidence=float(inter.get("confidence", 0.9))
            ))

        hypotheses = []
        for hyp in data.get("hypotheses", []):
            hypotheses.append(SemanticHypothesis(
                hypothesis_id=hyp.get("hypothesis_id", "hyp_x"),
                concept=hyp.get("concept", "unknown"),
                target_object_id=hyp.get("target_object_id"),
                expected_outcome=hyp.get("expected_outcome", "none"),
                status=hyp.get("status", "HYPOTHESIS"),
                confidence=float(hyp.get("confidence", 0.85))
            ))

        text_elements = []
        for txt in data.get("text_elements", []):
            lbox = tuple(txt["location_box"]) if txt.get("location_box") and len(txt["location_box"]) == 4 else None
            text_elements.append(SemanticText(
                content=txt.get("content", ""),
                location_box=lbox,
                language=txt.get("language", "pt-BR"),
                confidence=float(txt.get("confidence", 0.95))
            ))

        return SemanticObservation(
            scene_type=data.get("scene_type", "unknown"),
            objects=objects,
            relationships=relationships,
            possible_interactions=interactions,
            hypotheses=hypotheses,
            text_elements=text_elements,
            confidence=float(data.get("confidence", 0.9)),
            source="gemini_2.5_flash"
        )
