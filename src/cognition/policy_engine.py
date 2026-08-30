"""
Policy Engine - Motor de Políticas e Gatilhos (Triggers)
=========================================================

Permite registrar políticas reativas de comportamento no formato:
When(condition, action)

Exemplo:
"Quando aparecer Abra, me avisa."
--> PolicyTrigger(condition=lambda w: w.battle.opponent_name == "Abra", action="notify_player")

Autor: Klayton Companion Agent
Data: 2026-08-30
"""

from dataclasses import dataclass
from typing import Callable, List, Optional, Any
from ..world.world_state import WorldState
try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger("PolicyEngine")


@dataclass
class PolicyTrigger:
    name: str
    condition: Callable[[WorldState], bool]
    action_name: str
    active: bool = True


class PolicyEngine:
    """
    Motor de Políticas e Regras Reativas do Agente.
    """

    def __init__(self):
        self.triggers: List[PolicyTrigger] = []

    def add_trigger(self, name: str, condition: Callable[[WorldState], bool], action_name: str) -> None:
        trigger = PolicyTrigger(name=name, condition=condition, action_name=action_name)
        self.triggers.append(trigger)
        logger.info(f"⚡ Gatilho registrado: {name} ➔ Ação: {action_name}")

    def evaluate_triggers(self, world: WorldState) -> List[str]:
        """
        Avalia todas as políticas ativas contra o estado atual do mundo.
        Retorna lista de ações que devem ser disparadas imediatamente.
        """
        triggered_actions: List[str] = []
        for trigger in self.triggers:
            if trigger.active and trigger.condition(world):
                logger.info(f"🔔 Política ativada [{trigger.name}] ➔ Disparando ação: {trigger.action_name}")
                triggered_actions.append(trigger.action_name)
        return triggered_actions
