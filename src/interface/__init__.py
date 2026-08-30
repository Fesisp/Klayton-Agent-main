"""Módulo de Interface do Usuário e Voz do Klayton Agent."""
from .dialogue_manager import DialogueManager, SpeechUtterance
from .voice_listener import VoiceListener, TurnConsolidator

__all__ = [
    'DialogueManager',
    'SpeechUtterance',
    'VoiceListener',
    'TurnConsolidator',
]
