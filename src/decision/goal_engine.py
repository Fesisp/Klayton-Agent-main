"""
Goal Engine - Objetivos Parametrizados e Instanciáveis (GoalInstance)
=======================================================================

Evolui o sistema de Objetivos de um mero Enum estático para GoalInstance
com parâmetros dinâmicos, alvos específicos, restrições e condições de sucesso.

Exemplo:
GoalInstance(
    type=Goal.FARM_XP,
    target="Pikachu",
    target_level=35,
    location_hint="Viridian Forest",
    success_conditions={"level": 35}
)

Autor: Klayton Companion Agent
Data: 2026-08-30
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger("GoalEngine")


class Goal(Enum):
    """Tipos de Objetivos suportados."""
    IDLE = "IDLE"
    HUNT = "HUNT"
    FISH = "FISH"
    FARM_XP = "FARM_XP"
    PROGRESS_STORY = "PROGRESS_STORY"
    FOLLOW_PLAYER = "FOLLOW_PLAYER"
    TRAIN_POKEMON = "TRAIN_POKEMON"
    RETURN_TO_CENTER = "RETURN_TO_CENTER"
    BUY_ITEMS = "BUY_ITEMS"
    HEAL_TEAM = "HEAL_TEAM"

    @classmethod
    def from_string(cls, val: str) -> "Goal":
        val_upper = str(val).upper()
        if val_upper in cls.__members__:
            return cls[val_upper]
        legacy_map = {
            "MISSION": cls.PROGRESS_STORY,
            "HUNTING": cls.HUNT,
            "FOLLOW": cls.FOLLOW_PLAYER
        }
        return legacy_map.get(val_upper, cls.IDLE)


@dataclass
class GoalInstance:
    """
    Instância Parametrizada de um Objetivo com alvos, critérios de conclusão e restrições.
    """
    type: Goal
    target: Optional[str] = None                   # ex: "Pikachu", "Charmeleon"
    target_level: Optional[int] = None              # ex: 35
    location_hint: Optional[str] = None             # ex: "Viridian Forest"
    success_conditions: Dict[str, Any] = field(default_factory=dict)
    constraints: Dict[str, Any] = field(default_factory=dict)
    priority: float = 1.0

    @property
    def name(self) -> str:
        return self.type.name

    def is_fulfilled(self, world_state: Any) -> bool:
        """Verifica se as condições de sucesso da instância de objetivo foram atingidas."""
        if self.target_level and self.target:
            for member in getattr(world_state.team, 'members', []):
                if getattr(member, 'name', '').lower() == self.target.lower():
                    if getattr(member, 'level', 0) >= self.target_level:
                        return True
        return False


class GoalEngine:
    """Compatibilidade retroativa: empacota instâncias de objetivos."""
    def __init__(self, primary_goal: Goal = Goal.IDLE, config: Optional[Dict[str, Any]] = None):
        self.primary_goal = primary_goal
        self.config = config or {}

