"""
Goal Engine - Motor de Decisão Orientado a Objetivos
===================================================

Este módulo substitui a arquitetura imperativa baseada em Modos (BotBehavior)
por um sistema inteligente baseado em Objetivos (Goal-Oriented System).

Um Objetivo (Goal) define o RESULTADO DESEJADO e permite raciocínio dinâmico
para a escolha das melhores sub-ações e transições reativas.

Autor: PokeBot v3.0
Data: 2026-08-30
"""

from enum import Enum
from typing import Optional, Dict, Any
try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger("GoalEngine")


class Goal(Enum):
    """Objetivos suportados pelo bot."""
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
        # Mapeamento para retrocompatibilidade
        legacy_map = {
            "MISSION": cls.PROGRESS_STORY,
            "HUNTING": cls.HUNT,
            "FOLLOW": cls.FOLLOW_PLAYER
        }
        return legacy_map.get(val_upper, cls.IDLE)


class GoalEngine:
    """
    Motor de raciocínio que avalia o objetivo primário e o contexto do jogo
    para determinar a melhor ação/sub-goal ativa a cada frame ou iteração.
    """

    def __init__(self, primary_goal: Goal = Goal.IDLE, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.primary_goal = primary_goal
        self.override_subgoal: Optional[Goal] = None
        self.goal_context: Dict[str, Any] = {}
        logger.info(f"🎯 GoalEngine inicializado com Objetivo Primário: {self.primary_goal.name}")

    def set_primary_goal(self, goal: Goal) -> None:
        """Define um novo objetivo primário fornecido pelo usuário, UDP ou Hotkey."""
        if self.primary_goal != goal:
            logger.info(f"🎯 Alterando Objetivo Primário: {self.primary_goal.name} ➔ {goal.name}")
            self.primary_goal = goal
            self.override_subgoal = None

    def set_override_subgoal(self, subgoal: Optional[Goal]) -> None:
        """Define um sub-objetivo temporário que sobrepõe a execução normal."""
        if self.override_subgoal != subgoal:
            sub_name = subgoal.name if subgoal else "Nenhum"
            logger.info(f"⚡ Sub-objetivo temporário ajustado para: {sub_name}")
            self.override_subgoal = subgoal

    def evaluate_subgoal(self, context: Optional[Dict[str, Any]] = None) -> Goal:
        """
        Avalia o contexto do jogo (HP do time, se está em batalha, se perdeu alvo)
        e raciocina sobre qual Goal deve ser executado no ciclo atual.
        
        Args:
            context: Dicionário contendo dados de estado do jogo (ex: team_hp, in_battle, target_visible)
            
        Returns:
            Goal: O objetivo ativo a ser perseguido no momento.
        """
        context = context or {}
        self.goal_context = context

        # 1. Se houver um sub-goal sobrescrito ativamente
        if self.override_subgoal:
            return self.override_subgoal

        # 2. Raciocínio de emergência / necessidade vital:
        # Se o time estiver zerado/crítico de HP e o objetivo primário envolve combate/exploração
        team_needs_heal = context.get('team_needs_heal', False)
        if team_needs_heal and self.primary_goal in [Goal.HUNT, Goal.FISH, Goal.FARM_XP, Goal.PROGRESS_STORY, Goal.TRAIN_POKEMON]:
            logger.warning("🚑 Raciocínio de Emergência: Time necessita de cura! Trocando sub-goal para HEAL_TEAM.")
            return Goal.HEAL_TEAM

        # 3. Retorna o objetivo primário por padrão
        return self.primary_goal
