"""
Dialogue Manager & Thought-to-Speech (TTS)
===========================================

Traduz decisões e pensamentos internos do agente em falas públicas de intenção
("Thought -> Action -> Speech"), promovendo presença social e transparência de comportamento.

Exemplos:
- Decisão: Curar time -> Fala: "Minha equipe está meio machucada. Vou no Pokémon Center e já volto!"
- Decisão: Perdeu o líder -> Fala: "Te perdi de vista! Onde você foi?"
- Decisão: Novo Pokémon raro -> Fala: "Olha só! Apareceu um Pokémon diferente ali!"

Autor: Klayton Companion Agent
Data: 2026-08-30
"""

from dataclasses import dataclass
from typing import Optional
try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger("DialogueManager")


@dataclass
class SpeechUtterance:
    text: str
    emotion: str = "neutral"
    timestamp: float = 0.0


class DialogueManager:
    """
    Gerenciador de diálogo e expressão verbal do Companheiro.
    """

    def __init__(self, use_tts: bool = False):
        self.use_tts = use_tts
        self._last_speech: Optional[SpeechUtterance] = None

    def express_decision(self, decision_type: str, context: Optional[dict] = None) -> SpeechUtterance:
        """
        Gera uma fala natural pública a partir de um tipo de decisão interna.
        """
        context = context or {}
        speech_text = "Estou acompanhando você."

        if decision_type == "heal_needed":
            speech_text = "Minha equipe está meio machucada. Vou no Pokémon Center se curar rapidinho!"
        elif decision_type == "lost_player":
            speech_text = "Te perdi de vista! Onde você foi?"
        elif decision_type == "waiting_player":
            speech_text = "Tranquilo, vou ficar te esperando aqui."
        elif decision_type == "rare_pokemon":
            name = context.get('pokemon_name', 'raro')
            speech_text = f"Olha só! Apareceu um {name} ali!"
        elif decision_type == "personal_goal_start":
            goal = context.get('goal', 'meu objetivo')
            speech_text = f"Aproveitando que estamos aqui, vou trabalhar no meu objetivo de {goal}!"
        elif decision_type == "resume_follow":
            speech_text = "Beleza, vamos continuar juntos!"

        utterance = SpeechUtterance(text=speech_text)
        self._last_speech = utterance
        
        logger.info(f"🗣️ Klayton diz: '{speech_text}'")
        if self.use_tts:
            self._speak_tts(speech_text)

        return utterance

    def _speak_tts(self, text: str) -> None:
        """Interface de síntese de voz local (pyttsx3/SAPI5)."""
        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            logger.debug(f"TTS offline/não disponível: {e}")
