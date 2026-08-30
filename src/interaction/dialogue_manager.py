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

import difflib
from dataclasses import dataclass, field
from typing import Optional, List
from .neural_tts import NeuralTTSEngine
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

    def __init__(self, use_tts: bool = True):
        self.use_tts = use_tts
        self._last_speech: Optional[SpeechUtterance] = None
        self.recent_speech_history: List[str] = []
        
        # Motor Neural TTS com callbacks de estado
        self.tts_engine = NeuralTTSEngine(
            voice_name="pt-BR-AntonioNeural",
            on_speech_start=self._on_speech_start,
            on_speech_end=self._on_speech_end
        )

    @property
    def is_speaking(self) -> bool:
        return self.tts_engine.is_speaking

    def _on_speech_start(self) -> None:
        logger.debug("🔊 Klayton começou a falar (Supressão de eco ativada)")

    def _on_speech_end(self) -> None:
        logger.debug("🔇 Klayton terminou de falar")

    def is_echo_of_own_speech(self, text: str, similarity_threshold: float = 0.65) -> bool:
        """
        Verifica se o texto recebido é um eco ou repetição da própria fala recente do Klayton.
        """
        text_clean = text.strip().lower()
        if not text_clean:
            return False

        for past_speech in self.recent_speech_history:
            ratio = difflib.SequenceMatcher(None, text_clean, past_speech.lower()).ratio()
            if ratio >= similarity_threshold:
                logger.warning(f"🛡️ Eco de auto-fala detectado e suprimido: '{text}' (Similaridade {ratio*100:.0f}% com '{past_speech}')")
                return True
        return False

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
        
        # Guarda histórico para proteção de eco
        self.recent_speech_history.append(speech_text)
        if len(self.recent_speech_history) > 8:
            self.recent_speech_history.pop(0)

        logger.info(f"🗣️ Klayton diz: '{speech_text}'")
        if self.use_tts:
            self.tts_engine.speak(speech_text)

        return utterance
