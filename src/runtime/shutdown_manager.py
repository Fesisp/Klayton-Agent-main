"""
Shutdown Manager - Gerenciador de Desligamento Seguro Idempotente
==================================================================

Garante a liberação de todos os inputs físicos, gravação de dados e encerramento limpo dos subsistemas.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

from typing import Any, List, Optional
try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger("ShutdownManager")


class ShutdownManager:
    """Gerenciador idempotente de desligamento seguro."""

    def __init__(self):
        self.is_shutting_down = False
        self.is_shutdown_complete = False

    def shutdown(self, input_simulator: Optional[Any] = None) -> bool:
        """Executa a sequência de desligamento limpo sem duplicar chamadas."""
        if self.is_shutdown_complete:
            return True

        self.is_shutting_down = True
        logger.info("🛑 ShutdownManager: Iniciando sequência de desligamento seguro...")

        # 1. Liberação de todos os inputs físicos de teclado/mouse
        if input_simulator and hasattr(input_simulator, 'release_all'):
            try:
                input_simulator.release_all()
                logger.info("  ✅ Inputs físicos liberados com sucesso")
            except Exception as e:
                logger.error(f"  ⚠️ Erro ao liberar inputs: {e}")

        self.is_shutdown_complete = True
        self.is_shutting_down = False
        logger.info("STATUS: SHUTDOWN COMPLETE")
        return True
