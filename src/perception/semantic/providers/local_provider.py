"""
Local Vision Provider - Suporte Local para Qwen2.5-VL / Ollama
==============================================================

Implementa a integração com modelos locais de Visão e Linguagem (VLM), como
Qwen2.5-VL-7B-Instruct rodando via Ollama ou servidor local HTTP.

Servirá de fallback offline, reduzindo chamadas a APIs pagas e garantindo privacidade.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

import json
import base64
import io
from typing import Dict, Any, Optional
try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger("LocalVisionProvider")

from .base_provider import VisionLanguageProvider
from ..semantic_observation import SemanticObservation


class LocalVisionProvider(VisionLanguageProvider):
    """
    Provedor VLM local (Qwen2.5-VL-7B via Ollama / local HTTP endpoint).
    """

    def __init__(self, endpoint_url: Optional[str] = None, model_name: str = "qwen2.5-vl:7b", config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        local_cfg = self.config.get("semantic_ai", {}).get("local", {})
        self.endpoint_url = endpoint_url or local_cfg.get("endpoint", "http://localhost:11434/api/generate")
        self.model_name = local_cfg.get("model", model_name)

    async def analyze(self, image: Any, request_context: Optional[Dict[str, Any]] = None) -> SemanticObservation:
        """
        Envia a imagem para o servidor local VLM.
        """
        if image is None:
            return SemanticObservation(scene_type="unknown", confidence=0.0, source="local_no_image")

        try:
            import requests

            # Prepara imagem em base64
            img_b64 = ""
            if isinstance(image, bytes):
                img_b64 = base64.b64encode(image).decode('utf-8')
            elif hasattr(image, 'save'):  # PIL Image
                buf = io.BytesIO()
                image.save(buf, format="JPEG")
                img_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')

            if not img_b64:
                return SemanticObservation(scene_type="unknown", confidence=0.0, source="local_encode_error")

            payload = {
                "model": self.model_name,
                "prompt": "Analyze this game screenshot from PokeOne. Output valid JSON describing scene_type and objects.",
                "images": [img_b64],
                "stream": False,
                "format": "json"
            }

            res = requests.post(self.endpoint_url, json=payload, timeout=5.0)
            if res.status_code == 200:
                data = res.json()
                raw_text = data.get("response", "")
                if raw_text:
                    parsed = json.loads(raw_text)
                    return SemanticObservation(
                        scene_type=parsed.get("scene_type", "unknown"),
                        confidence=0.85,
                        source=f"local_vlm_{self.model_name}"
                    )

        except Exception as e:
            logger.debug(f"Provedor local VLM indisponível ({self.endpoint_url}): {e}")

        return SemanticObservation(
            scene_type="unknown",
            confidence=0.0,
            source="local_vlm_offline"
        )
