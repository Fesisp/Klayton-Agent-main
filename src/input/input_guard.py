"""
Input Guard - Guarda de Segurança de Inputs Físicos
===================================================

Aplica trava de liberação de teclas presas, limite de taxa de ações (15 acionamentos/s)
e atalho para Parada de Emergência (Ctrl+Shift+F12).

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

import time
from typing import Any, List, Optional
try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger("InputGuard")


class InputGuard:
    """Guarda de segurança para envio de teclas e acionamentos físicos."""

    def __init__(self, max_actions_per_second: int = 15):
        self.max_actions_per_second = max_actions_per_second
        self.action_timestamps: List[float] = []
        self.emergency_stop_active = False

    def allow_action(self) -> bool:
        """Verifica limite de taxa e estado da trava de emergência."""
        if self.emergency_stop_active:
            logger.warning("🛑 InputGuard: Ação bloqueada — Parada de Emergência Ativa!")
            return False

        now = time.time()
        self.action_timestamps = [t for t in self.action_timestamps if now - t <= 1.0]

        if len(self.action_timestamps) >= self.max_actions_per_second:
            logger.warning("⚠️ InputGuard: Limite de taxa de acionamento por segundo atingido!")
            return False

        self.action_timestamps.append(now)
        return True

    def trigger_emergency_stop(self, input_simulator: Optional[Any] = None) -> None:
        """Dispara a Parada de Emergência e solta todas as teclas imediatamente."""
        self.emergency_stop_active = True
        logger.error("🚨 EMERGENCY STOP DISPARADO! Soltando todas as teclas...")
        if input_simulator and hasattr(input_simulator, 'release_all'):
            try:
                input_simulator.release_all()
            except Exception as e:
                logger.error(f"Erro ao soltar teclas na Parada de Emergência: {e}")
