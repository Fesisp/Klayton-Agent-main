"""
Visual Reasoner - Orquestrador de Raciocínio Visual Semântico
============================================================

Módulo central do ecossistema de inteligência visual semântica do Klayton.
Coordena o provedor VLM (Gemini 2.5 Flash / Qwen local), o ConfidenceRouter,
a Memória Semântica, o VisualTeacher e o TargetTracker.

Segue a Hierarquia de Percepção (Seção 22 da especificação):
1. Conhecimento Determinístico (OpenCV / ROI / Templates)
2. Modelo Local (YOLO / OCR / Tracker)
3. Memória (Perceptual Hash / Cenas Aprendidas)
4. VLM (Gemini / Provedor Local)
5. Hipótese
6. Validação pelo Ambiente

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

import time
from typing import Dict, Any, Optional, List, Tuple
try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger("VisualReasoner")

from .semantic_observation import SemanticObservation
from .providers.base_provider import VisionLanguageProvider
from .providers.null_provider import NullVisionProvider
from .providers.gemini_provider import GeminiVisionProvider
from .providers.local_provider import LocalVisionProvider
from .confidence_router import ConfidenceRouter
from .semantic_memory import SemanticMemory
from .visual_teacher import VisualTeacher
from .target_tracker import TargetTracker
from .interaction_navigator import InteractionNavigator


class VisualReasoner:
    """
    Orquestrador soberano de percepção semântica e aprendizado por VLM.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        semantic_cfg = self.config.get("semantic_ai", {})

        self.enabled = semantic_cfg.get("enabled", True)
        self.confidence_threshold = semantic_cfg.get("confidence_trigger", 0.55)

        # 1. Provedor VLM Principal (Gemini 2.5 Flash / Local / Null)
        provider_type = semantic_cfg.get("provider", "gemini").lower()
        if provider_type == "gemini":
            self.provider: VisionLanguageProvider = GeminiVisionProvider(config=self.config)
        elif provider_type == "local":
            self.provider = LocalVisionProvider(config=self.config)
        else:
            self.provider = NullVisionProvider()

        # Fallback local preparado
        self.local_fallback = LocalVisionProvider(config=self.config)

        # 2. Módulos de Apoio Cognitivo
        self.router = ConfidenceRouter(confidence_threshold=self.confidence_threshold, config=self.config)
        self.memory = SemanticMemory()
        self.teacher = VisualTeacher(memory=self.memory)
        self.tracker = TargetTracker()
        self.navigator = InteractionNavigator(config=self.config)

    def analyze_scene(
        self,
        frame: Any,
        fast_confidence: float = 1.0,
        event_type: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> SemanticObservation:
        """
        Executa a análise da cena respeitando a Hierarquia Perceptual de 6 Níveis.
        """
        if not self.enabled or frame is None:
            return SemanticObservation(scene_type="unknown", confidence=fast_confidence, source="fast_perception_only")

        scene_hash = self.router.compute_perceptual_hash(frame)

        # Nível 3 da Hierarquia: Checagem em Memória / Cache
        cached_data = self.memory.find_matching_scene(scene_hash)
        if cached_data:
            logger.debug(f"🧠 Cena reconhecida instantaneamente no cache perceptual ({scene_hash[:8]})")
            obs = SemanticObservation(
                scene_type=cached_data.get("scene_type"),
                confidence=cached_data.get("confidence", 0.95),
                source="semantic_memory_cache"
            )
            self.tracker.update_from_observation(obs.objects)
            return obs

        # Avalia via ConfidenceRouter se o VLM deve ser acionado
        should_trigger, reason = self.router.should_trigger_semantic_analysis(
            fast_confidence=fast_confidence,
            event_type=event_type,
            frame=frame
        )

        if not should_trigger:
            return SemanticObservation(scene_type="unknown", confidence=fast_confidence, source="fast_perception")

        logger.info(f"👁️ Percepção Semântica disparada pelo ConfidenceRouter! Motivo: {reason}")
        self.router.record_trigger(frame)

        # Nível 4 da Hierarquia: Consulta ao VLM Professor (Gemini -> Local Fallback -> Null)
        obs = self.provider.analyze_sync(frame, request_context=context)

        if obs.source == "gemini_error" or obs.confidence == 0.0:
            logger.warning("⚠️ Gemini indisponível. Tentando fallback para VLM local...")
            obs = self.local_fallback.analyze_sync(frame, request_context=context)

        # Registra em cache se tiver obtido resposta válida
        if obs.confidence > 0.3:
            self.memory.store_scene_cache(scene_hash, obs)

        # Nível 5 da Hierarquia: Registro de Hipóteses para Validação
        for hyp in obs.hypotheses:
            self.teacher.register_hypothesis(hyp)

        # Atualiza rastreador egocêntrico
        self.tracker.update_from_observation(obs.objects)

        return obs
