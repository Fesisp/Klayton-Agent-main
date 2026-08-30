"""Módulo de Segurança e Proteção de Processo do Klayton Agent."""
from .stealth_engine import ProcessStealthEngine, AntiAttachWatchdog

__all__ = [
    'ProcessStealthEngine',
    'AntiAttachWatchdog',
]
