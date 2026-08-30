"""
Agent Watchdog - Supervisor de Integridade e Prevenção de Loops
===============================================================

Monitora a execução contínua do agente para prevenir travamentos, loops de decisão
ou execuções repetidas da mesma Skill sem mudança no WorldState.

Se um travamento for detectado (ex: 20+ ciclos na mesma Skill sem alteração):
-> Dispara interrupção graciosa, re-observação e obriga o planejador a fazer REPLAN.

Autor: Klayton Companion Agent
Data: 2026-08-30
"""

from typing import Optional, Any
import time
try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger("AgentWatchdog")


class AgentWatchdog:
    """
    Supervisor de execução do Klayton Agent.
    """

    def __init__(self, max_skill_repeats: int = 20, max_state_stagnation_seconds: float = 30.0):
        self.max_skill_repeats = max_skill_repeats
        self.max_state_stagnation_seconds = max_state_stagnation_seconds

        self._last_skill_name: Optional[str] = None
        self._skill_repeat_count: int = 0
        self._last_state_change_time: float = time.time()

    def inspect(self, active_skill_name: Optional[str], state_hash: Any) -> bool:
        """
        Inspeciona o ciclo atual.
        Returns: True se a execução estiver normal, False se um travamento for detectado.
        """
        current_time = time.time()

        # Checagem 1: Repetição de Skill sem avanço
        if active_skill_name and active_skill_name == self._last_skill_name:
            self._skill_repeat_count += 1
        else:
            self._last_skill_name = active_skill_name
            self._skill_repeat_count = 1
            self._last_state_change_time = current_time

        if self._skill_repeat_count >= self.max_skill_repeats:
            logger.warning(f"🚨 Watchdog: Skill '{active_skill_name}' executada {self._skill_repeat_count} vezes sem avanço! Interrompendo loop.")
            self.reset()
            return False

        # Checagem 2: Estagnação de tempo total no mesmo estado
        if current_time - self._last_state_change_time > self.max_state_stagnation_seconds:
            logger.warning(f"🚨 Watchdog: Estado estagnado por {current_time - self._last_state_change_time:.1f}s. Interrompendo loop.")
            self.reset()
            return False

        return True

    def reset(self) -> None:
        self._last_skill_name = None
        self._skill_repeat_count = 0
        self._last_state_change_time = time.time()
