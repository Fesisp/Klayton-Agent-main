"""
Neural TTS Engine - Síntese de Voz Neural Gratuita e de Alta Qualidade
======================================================================

Utiliza o Edge-TTS da Microsoft (vozes neurais brasileiras gratuitas como 'pt-BR-AntonioNeural')
com fallback automático para pyttsx3 / SAPI5 nativo caso offline.

Executa a reprodução em thread assíncrona não-bloqueante para não travar a execução do agente.

Autor: Klayton Companion Agent Framework
Data: 2026-08-30
"""

import asyncio
import os
import tempfile
import threading
import time
from typing import Optional, Callable
try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger("NeuralTTS")


class NeuralTTSEngine:
    """
    Motor de Síntese Neural Gratuito de Voz.
    """

    def __init__(self, voice_name: str = "pt-BR-AntonioNeural", rate: str = "+0%", on_speech_start: Optional[Callable[[], None]] = None, on_speech_end: Optional[Callable[[], None]] = None):
        self.voice_name = voice_name
        self.rate = rate
        self.on_speech_start = on_speech_start
        self.on_speech_end = on_speech_end
        self.is_speaking = False

    def speak(self, text: str) -> None:
        """Dispara a fala em uma thread não-bloqueante."""
        if not text.strip():
            return
        threading.Thread(target=self._speak_worker, args=(text,), daemon=True, name="NeuralTTSWorker").start()

    def _speak_worker(self, text: str) -> None:
        self.is_speaking = True
        if self.on_speech_start:
            try:
                self.on_speech_start()
            except Exception:
                pass

        spoken = False
        # 1. Tenta sintetizar com Edge-TTS (Neural de alta fidelidade)
        try:
            import edge_tts
            spoken = self._speak_with_edge_tts(text)
        except Exception as e:
            logger.debug(f"Edge-TTS indisponível: {e}")

        # 2. Fallback para pyttsx3 se Edge-TTS falhar ou estiver offline
        if not spoken:
            self._speak_with_pyttsx3(text)

        # Pequeno cooldown para supressão de eco
        time.sleep(0.3)
        self.is_speaking = False
        if self.on_speech_end:
            try:
                self.on_speech_end()
            except Exception:
                pass

    def _speak_with_edge_tts(self, text: str) -> bool:
        """Gera áudio via Edge-TTS e reproduz."""
        try:
            import edge_tts
            import pygame
            
            # Inicializa pygame mixer se necessário
            if not pygame.mixer.get_init():
                pygame.mixer.init()

            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as fp:
                temp_path = fp.name

            async def _generate():
                communicate = edge_tts.Communicate(text, self.voice_name, rate=self.rate)
                await communicate.save(temp_path)

            asyncio.run(_generate())

            if os.path.exists(temp_path):
                pygame.mixer.music.load(temp_path)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    time.sleep(0.05)
                pygame.mixer.music.unload()
                try:
                    os.remove(temp_path)
                except Exception:
                    pass
                return True
        except Exception as e:
            logger.debug(f"Falha na reprodução Edge-TTS: {e}")
        return False

    def _speak_with_pyttsx3(self, text: str) -> None:
        """Fallback nativo via pyttsx3."""
        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            logger.debug(f"pyttsx3 indisponível: {e}")
