"""
GOAP Planner - Goal-Oriented Action Planning
==============================================

Constrói sequências dinâmicas de Skills para atingir um determinado Goal.
Suporta o ciclo de REPLAN contínuo quando o WorldState altera.

Autor: Klayton Agent 2.0 Framework
Data: 2026-08-30
"""

from typing import List, Optional, Dict, Any
from ..world.world_state import WorldState
from ..skills.base_skill import BaseSkill
from ..skills.battle_skill import BattleSkill
from ..skills.hunting_skill import HuntingSkill
try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger("GOAPPlanner")


class GOAPPlanner:
    """
    Planejador GOAP que traduz Goals e WorldState em uma fila sequencial de Skills.
    """

    def __init__(self):
        self.available_skills: Dict[str, BaseSkill] = {
            "BattleSkill": BattleSkill(),
            "HuntingSkill": HuntingSkill(),
        }
        self.current_plan: List[BaseSkill] = []
        self.needs_replan: bool = True

    def trigger_replan(self) -> None:
        """Força a reconstrução do plano no próximo ciclo."""
        logger.info("🔄 GOAPPlanner: Re-planejamento (REPLAN) solicitado!")
        self.needs_replan = True

    def build_plan(self, goal_name: str, world: WorldState) -> List[BaseSkill]:
        """
        Gera a sequência de Skills ideal para alcançar o objetivo em questão.
        """
        plan: List[BaseSkill] = []

        # 1. Checagem de sobrevivência/emergência suprime o plano original
        if world.team.needs_healing and goal_name not in ["HEAL_TEAM", "IDLE"]:
            logger.warning("🚑 GOAPPlanner: Time em situação crítica! Priorizando desvio para cura.")
            # Insere habilidade de caça/retorno prévia
            if "HuntingSkill" in self.available_skills:
                plan.append(self.available_skills["HuntingSkill"])
            self.current_plan = plan
            self.needs_replan = False
            return plan

        # 2. Se em batalha, a prioridade absoluta é a BattleSkill
        if world.battle.in_battle:
            if "BattleSkill" in self.available_skills:
                plan.append(self.available_skills["BattleSkill"])
            self.current_plan = plan
            self.needs_replan = False
            return plan

        # 3. Mapeamento de Goals para sequências de Skills
        if goal_name in ["HUNT", "FARM_XP", "TRAIN_POKEMON"]:
            if "HuntingSkill" in self.available_skills:
                plan.append(self.available_skills["HuntingSkill"])

        self.current_plan = plan
        self.needs_replan = False
        return plan

    def get_next_skill(self, goal_name: str, world: WorldState) -> Optional[BaseSkill]:
        """
        Retorna a próxima Skill pronta para ser executada, reconstruindo o plano se necessário.
        """
        if self.needs_replan or not self.current_plan:
            self.build_plan(goal_name, world)

        if self.current_plan:
            skill = self.current_plan[0]
            if skill.is_complete(world):
                self.current_plan.pop(0)
                return self.get_next_skill(goal_name, world)
            return skill

        return None
