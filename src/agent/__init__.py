"""Módulo do Agente Autônomo e Companheiro do Klayton Agent."""
from .agent import KlaytonAgent
from .companion_agent import KlaytonCompanionAgent
from .goal_manager import CompanionGoalManager, PersonalGoal

__all__ = [
    'KlaytonAgent',
    'KlaytonCompanionAgent',
    'CompanionGoalManager',
    'PersonalGoal',
]
