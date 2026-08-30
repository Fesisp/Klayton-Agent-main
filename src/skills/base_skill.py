"""
Base Skill - Interface Base de Capacidades
==========================================

Define a interface padrão para todas as Skills do Klayton Agent 2.0.

Cada Skill é uma capacidade modular de execução (ex: Battle, Hunting, Follow, Fishing),
desacoplada da lógica de decisão do planejador.

Autor: Klayton Agent 2.0 Framework
Data: 2026-08-30
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Optional
from enum import Enum


class SkillStatus(Enum):
    """Status explícito de retorno de uma Skill."""
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    RUNNING = "RUNNING"
    INTERRUPTED = "INTERRUPTED"


@dataclass
class SkillResult:
    """Resultado da execução de um ciclo da Skill."""
    status: SkillStatus = SkillStatus.RUNNING
    message: str = ""
    data: Dict[str, Any] = None

    @property
    def success(self) -> bool:
        return self.status == SkillStatus.SUCCESS

    @property
    def failed(self) -> bool:
        return self.status == SkillStatus.FAILED


class BaseSkill(ABC):
    """Classe abstrata base para todas as Skills."""

    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        self.name = name
        self.config = config or {}

    @abstractmethod
    def can_execute(self, world: WorldState) -> bool:
        """Verifica se as pré-condições para executar a Skill estão satisfeitas."""
        pass

    @abstractmethod
    def execute(self, world: WorldState, components: Dict[str, Any]) -> SkillResult:
        """Executa um ciclo da Skill utilizando os componentes de ação/percepção."""
        pass

    @abstractmethod
    def is_complete(self, world: WorldState) -> bool:
        """Verifica se o objetivo da Skill foi concluído."""
        pass
