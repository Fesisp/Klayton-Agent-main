"""
Movement Verifier - Verificação de Movimento e Obstáculos
==========================================================

Verifica se a ação de movimento realmente alterou a posição do personagem no frame seguinte.
Se a posição se mantiver idêntica após múltiplos comandos, sinaliza obstáculo e solicita escape/replan.

Autor: Klayton Companion Agent
Data: 2026-08-30
"""

from typing import Tuple, Optional
import time


class MovementVerifier:
    """
    Verificador contínuo de movimentação.
    """

    def __init__(self, max_stuck_attempts: int = 3):
        self.max_stuck_attempts = max_stuck_attempts
        self.last_position: Optional[Tuple[int, int]] = None
        self.stuck_counter: int = 0

    def verify(self, current_pos: Tuple[int, int]) -> bool:
        """
        Verifica se houve movimento.
        Returns: True se movimentou com sucesso, False se travou no mesmo ponto.
        """
        if self.last_position is None:
            self.last_position = current_pos
            self.stuck_counter = 0
            return True

        if current_pos == self.last_position:
            self.stuck_counter += 1
        else:
            self.last_position = current_pos
            self.stuck_counter = 0
            return True

        return self.stuck_counter < self.max_stuck_attempts

    @property
    def is_stuck(self) -> bool:
        return self.stuck_counter >= self.max_stuck_attempts

    def reset(self) -> None:
        self.last_position = None
        self.stuck_counter = 0
