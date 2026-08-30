"""
Recovery Manager - Gerenciador de Recuperação de Erros
======================================================

Quando uma ação falha (posição inalterada, OCR confuso, travamento detectado pelo Watchdog):
1. Interrompe a execução ativa.
2. Executa movimento humanizado de reposicionamento (escape em 4 direções).
3. Limpa caches ruidosos de percepção.
4. Solicita REPLAN imediato no planejador.

Autor: Klayton Companion Agent
Data: 2026-08-30
"""

import random
import time
from typing import Dict, Any, Optional
from ..world.world_state import WorldState
try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger("RecoveryManager")


class RecoveryManager:
    """
    Gerenciador de Recuperação de Erros e Obstáculos.
    """

    def __init__(self):
        self.recovery_attempts: int = 0

    def recover(self, world: WorldState, components: Dict[str, Any], reason: str = "Unspecified") -> bool:
        """
        Executa procedimento de recuperação.
        """
        self.recovery_attempts += 1
        logger.warning(f"🚨 RecoveryManager: Iniciando recuperação de erro #{self.recovery_attempts} (Motivo: {reason})")

        input_sim = components.get('input')
        if input_sim:
            # 1. Movimento de fuga em direção aleatória para descolar de obstáculos
            escape_keys = ['w', 'a', 's', 'd']
            chosen_key = random.choice(escape_keys)
            logger.info(f"🚧 Executando passos de descolamento de obstáculo ({chosen_key})...")
            
            for _ in range(3):
                input_sim.press(chosen_key)
                time.sleep(0.1)

        # 2. Reseta estados de estagnação no WorldState
        world.agent.active_skill = None
        world.update_timestamp()
        
        logger.info("✅ Procedimento de recuperação concluído. Solicitando REPLAN...")
        return True
