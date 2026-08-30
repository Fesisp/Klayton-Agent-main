"""
Voice Listener & Turn Consolidator
==================================

Sub-sistema de escuta contínua de voz e transcrição em tempo real (baseado no projeto Interview/EchoPilot).

Componentes principais:
1. TurnConsolidator: Agregador de turnos de fala com debounce adaptativo e análise de tokens conectivos
   ("e", "mas", "porque", "então", "que") para evitar respostas prematuras antes da frase terminar.
2. VoiceListener: Capturador contínuo em thread separada com repasse automático ao KlaytonCompanionAgent.

Autor: Klayton Companion Agent Framework
Data: 2026-08-30
"""

import io
import time
import wave
import threading
from typing import Callable, Optional, List
import numpy as np
try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger("VoiceListener")


# Tokens conectivos em PT-BR indicando continuidade de fala
CONNECTIVE_TOKENS = {
    "e", "mas", "porque", "por que", "pois", "que", "quando", "se", "como", "onde",
    "então", "ou", "além disso", "tipo", "por exemplo", "também", "aí"
}


class TurnConsolidator:
    """
    Agregador inteligente de fragmentos de fala.
    Combina falas longas sem disparar respostas prematuras da IA.
    """

    def __init__(self, debounce_sec: float = 1.3, on_turn_ready_callback: Optional[Callable[[str], None]] = None):
        self.debounce_sec = debounce_sec
        self.on_turn_ready = on_turn_ready_callback
        self.current_fragments: List[str] = []
        self._timer: Optional[threading.Timer] = None
        self._lock = threading.Lock()

    def add_fragment(self, text: str) -> None:
        cleaned = text.strip()
        if not cleaned:
            return

        with self._lock:
            self.current_fragments.append(cleaned)

            if self._timer and self._timer.is_alive():
                self._timer.cancel()

            last_word = cleaned.split()[-1].lower().rstrip(".,?!;:")
            is_connective = last_word in CONNECTIVE_TOKENS
            ends_with_question = cleaned.endswith("?")

            if is_connective:
                wait_time = self.debounce_sec + 0.6
            elif ends_with_question:
                wait_time = max(0.8, self.debounce_sec - 0.4)
            else:
                wait_time = self.debounce_sec

            self._timer = threading.Timer(wait_time, self._flush_turn)
            self._timer.daemon = True
            self._timer.start()

    def _flush_turn(self) -> None:
        with self._lock:
            if not self.current_fragments:
                return
            full_sentence = " ".join(self.current_fragments)
            self.current_fragments = []

        if self.on_turn_ready and len(full_sentence.strip()) > 2:
            logger.info(f"🎙️ Turno de fala consolidado: '{full_sentence}'")
            self.on_turn_ready(full_sentence)


class VoiceListener:
    """
    Orquestrador do Listener de Voz do Klayton.
    """

    def __init__(self, agent_callback: Optional[Callable[[str], str]] = None, language: str = "pt-BR"):
        self.agent_callback = agent_callback
        self.language = language
        self.running: bool = False
        self.turn_consolidator = TurnConsolidator(
            debounce_sec=1.2,
            on_turn_ready_callback=self._on_speech_consolidated
        )

    def process_audio_text(self, text_fragment: str) -> None:
        """
        Recebe fragmento de texto transcrito e envia para o consolidador de turnos.
        """
        self.turn_consolidator.add_fragment(text_fragment)

    def _on_speech_consolidated(self, full_sentence: str) -> None:
        """
        Callback executado quando uma frase completa é consolidada.
        """
        if self.agent_callback:
            response = self.agent_callback(full_sentence)
            logger.info(f"🗣️ Resposta verbal do Klayton: '{response}'")
