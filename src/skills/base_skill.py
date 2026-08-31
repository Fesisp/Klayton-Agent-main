"""
Base Skill - Interface Base Universal de Capacidades
==================================================

Define o contrato padronizado de interface para todas as Skills do Klayton Agent.
Oferece ciclo de vida completo:
- can_start / can_execute
- start
- update / execute
- cancel
- recover
- status

Status suportados: READY, RUNNING, SUCCESS, FAILED, INTERRUPTED, BLOCKED.

Autor: Klayton Agent 2.0 Framework
Data: 2026-08-30
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Optional
from enum import Enum
from ..world.world_state import WorldState


class SkillStatus(Enum):
    """Status padronizado universal para o motor de Skills do Klayton."""
    READY = "READY"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    INTERRUPTED = "INTERRUPTED"
    BLOCKED = "BLOCKED"


@dataclass
class SkillResult:
    """Resultado da execução de um ciclo de Skill."""
    status: SkillStatus = SkillStatus.RUNNING
    message: str = ""
    data: Dict[str, Any] = field(default_factory=dict)

    @property
    def success(self) -> bool:
        return self.status == SkillStatus.SUCCESS

    @property
    def failed(self) -> bool:
        return self.status in [SkillStatus.FAILED, SkillStatus.BLOCKED]


class BaseSkill(ABC):
    """Classe abstrata base com contrato completo de ciclo de vida de Skill."""

    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        self.name = name
        self.config = config or {}
        self.target_pokemon: Optional[str] = None
        self.target_level: Optional[int] = None
        self.target_map: Optional[str] = None
        self._current_status: SkillStatus = SkillStatus.READY

    def reset_runtime_state(self) -> None:
        """Reseta variáveis transitórias de estado antes da reativação da Skill."""
        self._current_status = SkillStatus.READY
        self.target_pokemon = None
        self.target_level = None
        self.target_map = None

    def can_start(self, world: WorldState) -> bool:
        """Verifica se a Skill pode ser iniciada no estado atual do mundo."""
        return self.can_execute(world)

    def start(self, context: Dict[str, Any]) -> None:
        """Inicializa o contexto de execução da Skill."""
        self._current_status = SkillStatus.RUNNING

    def update(self, world: WorldState, components: Dict[str, Any]) -> SkillResult:
        """Executa a atualização de um ciclo da Skill."""
        res = self.execute(world, components)
        self._current_status = res.status
        return res

    def cancel(self, world: WorldState) -> None:
        """Interrompe graciosamente a execução da Skill."""
        self._current_status = SkillStatus.INTERRUPTED

    def recover(self, world: WorldState) -> None:
        """Aplica estratégias de recuperação interna da Skill."""
        self._current_status = SkillStatus.READY

    def status(self) -> SkillStatus:
        """Retorna o status atual de execução da Skill."""
        return self._current_status

    @abstractmethod
    def can_execute(self, world: WorldState) -> bool:
        pass

    @abstractmethod
    def execute(self, world: WorldState, components: Dict[str, Any]) -> SkillResult:
        pass

    def is_complete(self, world: WorldState) -> bool:
        if self.target_level and self.target_pokemon:
            for member in getattr(world.team, 'members', []):
                if getattr(member, 'name', '').lower() == self.target_pokemon.lower() and getattr(member, 'level', 0) >= self.target_level:
                    return True
        return self._current_status == SkillStatus.SUCCESS
