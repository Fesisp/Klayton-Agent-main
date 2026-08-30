"""
Event Bus - Barramento de Eventos Desacoplado
==============================================

Sistema de publicação e subscrição (Pub/Sub) para desacoplar a percepção,
o modelo de mundo, o planejador e os componentes de ação.

Permite reatividade em tempo real sem chamadas diretas rígidas.

Autor: Klayton Agent 2.0 Framework
Data: 2026-08-30
"""

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Type, Any
import time
try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger("EventBus")


@dataclass
class Event:
    """Evento base do barramento."""
    timestamp: float = field(default_factory=time.time)


@dataclass
class PokemonEncounteredEvent(Event):
    name: str = "Unknown"
    level: int = 1
    is_shiny: bool = False


@dataclass
class BattleStartedEvent(Event):
    opponent_name: str = "Unknown"


@dataclass
class BattleEndedEvent(Event):
    victory: bool = True


@dataclass
class LowHealthEvent(Event):
    pokemon_name: str = "Unknown"
    hp_percentage: float = 0.0


@dataclass
class GoalChangedEvent(Event):
    old_goal: str = "IDLE"
    new_goal: str = "IDLE"


@dataclass
class VoiceCommandReceivedEvent(Event):
    raw_text: str = ""
    intent_action: str = ""


class EventBus:
    """
    Barramento de eventos com suporte a subscrição por tipo de evento.
    """

    def __init__(self):
        self._subscribers: Dict[Type[Event], List[Callable[[Any], None]]] = {}

    def subscribe(self, event_type: Type[Event], handler: Callable[[Any], None]) -> None:
        """Inscreve um callback para um tipo de evento."""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)
        logger.debug(f"📡 Callback inscrito para evento: {event_type.__name__}")

    def unsubscribe(self, event_type: Type[Event], handler: Callable[[Any], None]) -> None:
        """Remove a inscrição de um callback."""
        if event_type in self._subscribers and handler in self._subscribers[event_type]:
            self._subscribers[event_type].remove(handler)

    def publish(self, event: Event) -> None:
        """Publica um evento para todos os inscritos do seu tipo."""
        event_type = type(event)
        handlers = self._subscribers.get(event_type, [])
        if handlers:
            logger.info(f"📢 Publicando evento [{event_type.__name__}] para {len(handlers)} inscritos")
            for handler in handlers:
                try:
                    handler(event)
                except Exception as e:
                    logger.error(f"❌ Erro ao executar handler de evento [{event_type.__name__}]: {e}")
