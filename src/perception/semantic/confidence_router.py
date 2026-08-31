"""
Confidence Router & Budget Manager
==================================

Gerencia e roteia o disparo da Percepção Semântica (VLM / Gemini) baseado em:
1. Nível de confiança da percepção rápida (< 0.55).
2. Eventos críticos (UNKNOWN_SCENE, PLAYER_LOST, UNIDENTIFIED_NPC, FAILED_INTERACTION).
3. Hash Perceptual da cena (evita reconsultar a mesma cena em menos de 30s).
4. Limite de orçamento (SemanticBudget: max 8 req/min) e cooldown de 2.0s.
5. Privacidade (recorte egocêntrico da janela do PokeOne).

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

import time
import hashlib
from typing import Dict, Any, Optional, List, Tuple
try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger("ConfidenceRouter")


class SemanticBudget:
    """Gerenciador de orçamento de requisições VLM."""

    def __init__(self, max_per_minute: int = 8, cooldown_seconds: float = 2.0, duplicate_seconds: float = 30.0):
        self.max_per_minute = max_per_minute
        self.cooldown_seconds = cooldown_seconds
        self.duplicate_seconds = duplicate_seconds

        self.request_timestamps: List[float] = []
        self.last_request_time: float = 0.0
        self.seen_scene_hashes: Dict[str, float] = {}

    def can_request(self, scene_hash: Optional[str] = None) -> Tuple[bool, str]:
        """Avalia se uma nova análise semântica pode ser realizada."""
        now = time.time()

        # 1. Cooldown básico entre chamadas (2s)
        if (now - self.last_request_time) < self.cooldown_seconds:
            return False, f"cooldown_active ({self.cooldown_seconds - (now - self.last_request_time):.1f}s restantes)"

        # 2. Limite de requisições por minuto (max 8)
        self.request_timestamps = [t for t in self.request_timestamps if (now - t) < 60.0]
        if len(self.request_timestamps) >= self.max_per_minute:
            return False, f"rate_limit_per_minute_reached ({len(self.request_timestamps)}/{self.max_per_minute})"

        # 3. Cache de cena duplicada (30s)
        if scene_hash:
            last_seen = self.seen_scene_hashes.get(scene_hash, 0.0)
            if (now - last_seen) < self.duplicate_seconds:
                return False, f"duplicate_scene_cached ({self.duplicate_seconds - (now - last_seen):.1f}s restantes)"

        return True, "allowed"

    def record_request(self, scene_hash: Optional[str] = None) -> None:
        """Registra a execução de uma requisição VLM."""
        now = time.time()
        self.last_request_time = now
        self.request_timestamps.append(now)
        if scene_hash:
            self.seen_scene_hashes[scene_hash] = now


class ConfidenceRouter:
    """
    Roteador de confiança e disparador por eventos para a Percepção Semântica.
    """

    TRIGGER_EVENTS = {
        "UNKNOWN_SCENE", "UNKNOWN_OBJECT", "UNKNOWN_UI", "AMBIGUOUS_TARGET",
        "FAILED_INTERACTION", "REPEATED_NAVIGATION_FAILURE", "NEW_MAP",
        "UNIDENTIFIED_DIALOG", "UNIDENTIFIED_NPC", "PLAYER_LOST"
    }

    def __init__(self, confidence_threshold: float = 0.55, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        semantic_cfg = self.config.get("semantic_ai", {})
        self.confidence_threshold = semantic_cfg.get("confidence_trigger", confidence_threshold)

        max_req = semantic_cfg.get("max_requests_per_minute", 8)
        cooldown = semantic_cfg.get("cooldown_seconds", 2.0)
        dup_sec = semantic_cfg.get("duplicate_scene_seconds", 30.0)

        self.budget = SemanticBudget(
            max_per_minute=max_req,
            cooldown_seconds=cooldown,
            duplicate_seconds=dup_sec
        )

    def compute_perceptual_hash(self, frame: Any) -> str:
        """Calcula uma impressão digital (hash perceptual simples) do frame."""
        if frame is None:
            return "empty_frame"
        try:
            # Se for numpy ndarray, calcula hash de amostras em resolução reduzida
            import numpy as np
            if isinstance(frame, np.ndarray):
                # Reduz amostragem 16x16 em tons de cinza para perceptual hash rápido
                import cv2
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) if len(frame.shape) == 3 else frame
                resized = cv2.resize(gray, (16, 16), interpolation=cv2.INTER_AREA)
                avg = resized.mean()
                bits = resized > avg
                return hashlib.md5(bits.tobytes()).hexdigest()
        except Exception:
            pass

        # Fallback para hash genérico de str / bytes
        if isinstance(frame, bytes):
            return hashlib.md5(frame[:4096]).hexdigest()
        return str(hash(str(frame)))

    def should_trigger_semantic_analysis(
        self,
        fast_confidence: float,
        event_type: Optional[str] = None,
        frame: Any = None
    ) -> Tuple[bool, str]:
        """
        Decide se a Percepção Semântica VLM deve ser ativada.
        """
        scene_hash = self.compute_perceptual_hash(frame)

        # 1. Checagem de Orçamento e Cooldown
        allowed, reason = self.budget.can_request(scene_hash)
        if not allowed:
            return False, f"budget_blocked: {reason}"

        # 2. Disparo por evento crítico explícito
        if event_type and event_type.upper() in self.TRIGGER_EVENTS:
            return True, f"event_trigger: {event_type}"

        # 3. Disparo por confiança baixa da percepção rápida (< 0.55)
        if fast_confidence < self.confidence_threshold:
            return True, f"low_confidence_trigger: {fast_confidence:.2f} < {self.confidence_threshold:.2f}"

        return False, f"fast_perception_sufficient ({fast_confidence:.2f} >= {self.confidence_threshold:.2f})"

    def record_trigger(self, frame: Any = None) -> None:
        """Registra o disparo autorizado no orçamento."""
        scene_hash = self.compute_perceptual_hash(frame)
        self.budget.record_request(scene_hash)
