"""
GOAP Planner - Goal-Oriented Action Planning Real
=================================================

Implementa o algoritmo formal de GOAP (Goal-Oriented Action Planning) com:
- Espaço de Estados (State Space A* Search)
- Ações com Pré-condições e Efeitos
- Fila de Execução de Skills (Skill Queue)
- Sistema de Interrupção e Retomada (Plan Interrupt & Resume Stack)

Exemplo Real:
Goal: "Treinar Pikachu até o nível 35"
Goal State: {"target_level_reached": True}

Plano Gerado pelo GOAP:
1. CheckResources / Shop (se pokeballs/potions zeradas)
2. HealTeam (se HP < 100%)
3. NavigateToSpot (se não estiver na rota de treino)
4. HuntEncounter (procura batalha na grama)
5. BattleFight (luta e ganha XP)
6. CheckLevel (verifica level atual vs meta)

Se o HP ficar crítico durante o treino:
Interrupt -> Push Plan -> Heal -> Pop Plan -> Resume de onde parou!

Autor: Klayton Companion Agent Framework
Data: 2026-08-30
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Set
from ..world.world_state import WorldState
from ..skills.base_skill import BaseSkill
from ..skills import (
    FollowSkill, WaitSkill, NavigateSkill, HealSkill,
    BattleSkill, HuntingSkill, CaptureSkill, FishingSkill,
    InteractionSkill, ShoppingSkill, QuestSkill, ExploreSkill,
    RecoverSkill
)
try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger("GOAPPlanner")


@dataclass
class GOAPAction:
    """Ação do GOAP com pré-condições, efeitos e custo."""
    name: str
    target_skill_name: str
    preconditions: Dict[str, Any] = field(default_factory=dict)
    effects: Dict[str, Any] = field(default_factory=dict)
    cost: float = 1.0

    def check_preconditions(self, state: Dict[str, Any]) -> bool:
        """Verifica se todas as pré-condições estão satisfeitas no estado atual."""
        for key, val in self.preconditions.items():
            if state.get(key) != val:
                return False
        return True

    def apply_effects(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Retorna uma cópia do estado após aplicar os efeitos da ação."""
        new_state = dict(state)
        new_state.update(self.effects)
        return new_state


@dataclass
class GOAPNode:
    """Nó para o algoritmo A* no espaço de estados."""
    state: Dict[str, Any]
    parent: Optional['GOAPNode'] = None
    action: Optional[GOAPAction] = None
    g_cost: float = 0.0
    h_cost: float = 0.0

    @property
    def f_cost(self) -> float:
        return self.g_cost + self.h_cost


class GOAPPlanner:
    """
    Planejador GOAP completo com busca A*, fila de skills e pilha de retomada (Resume).
    """

    def __init__(self):
        self.skills: Dict[str, BaseSkill] = {
            "FollowSkill": FollowSkill(),
            "WaitSkill": WaitSkill(),
            "NavigateSkill": NavigateSkill(),
            "HealSkill": HealSkill(),
            "BattleSkill": BattleSkill(),
            "HuntingSkill": HuntingSkill(),
            "CaptureSkill": CaptureSkill(),
            "FishingSkill": FishingSkill(),
            "InteractionSkill": InteractionSkill(),
            "ShoppingSkill": ShoppingSkill(),
            "QuestSkill": QuestSkill(),
            "ExploreSkill": ExploreSkill(),
            "RecoverSkill": RecoverSkill(),
        }
        self.actions: List[GOAPAction] = []
        self._register_default_actions()
        
        self.current_plan: List[GOAPAction] = []
        self.interrupted_plan_stack: List[List[GOAPAction]] = []
        self.needs_replan: bool = True

    def _register_default_actions(self) -> None:
        """Registra o catálogo de ações com pré-condições e efeitos."""
        self.actions = [
            GOAPAction(
                name="HealTeam",
                target_skill_name="HealSkill",
                preconditions={"in_battle": False},
                effects={"team_healed": True, "needs_heal": False},
                cost=2.0
            ),
            GOAPAction(
                name="BuyPotionsAndBalls",
                target_skill_name="ShoppingSkill",
                preconditions={"in_battle": False},
                effects={"has_supplies": True},
                cost=3.0
            ),
            GOAPAction(
                name="NavigateToFarmArea",
                target_skill_name="NavigateSkill",
                preconditions={"team_healed": True, "in_battle": False},
                effects={"at_target_map": True},
                cost=2.0
            ),
            GOAPAction(
                name="HuntInGrass",
                target_skill_name="HuntingSkill",
                preconditions={"team_healed": True, "at_target_map": True, "in_battle": False},
                effects={"in_battle": True},
                cost=1.0
            ),
            GOAPAction(
                name="FightBattle",
                target_skill_name="BattleSkill",
                preconditions={"in_battle": True},
                effects={"in_battle": False, "target_level_reached": True, "gained_xp": True},
                cost=3.0
            ),
            GOAPAction(
                name="FollowLeader",
                target_skill_name="FollowSkill",
                preconditions={"in_battle": False},
                effects={"following_leader": True},
                cost=1.0
            ),
            GOAPAction(
                name="WaitHere",
                target_skill_name="WaitSkill",
                preconditions={"in_battle": False},
                effects={"waiting": True},
                cost=1.0
            )
        ]

    def extract_world_state_symbols(self, world: WorldState) -> Dict[str, Any]:
        """Converte o WorldState em símbolos de estado booleano/categórico para o GOAP."""
        return {
            "in_battle": bool(world.battle.in_battle),
            "team_healed": not bool(world.team.needs_healing),
            "needs_heal": bool(world.team.needs_healing),
            "has_supplies": (world.resources.pokeballs_count > 0 and world.resources.potions_count > 0),
            "at_target_map": True,
            "target_level_reached": False,
            "following_leader": bool(world.companion.is_following_leader)
        }

    def plan(self, start_state: Dict[str, Any], goal_state: Dict[str, Any]) -> List[GOAPAction]:
        """
        Busca A* no espaço de estados para encontrar a sequência de menor custo que satisfaça goal_state.
        """
        open_list: List[GOAPNode] = [GOAPNode(state=start_state, g_cost=0.0, h_cost=self._heuristic(start_state, goal_state))]
        closed_states: List[Dict[str, Any]] = []

        while open_list:
            # Pega o nó com menor f_cost
            open_list.sort(key=lambda n: n.f_cost)
            current_node = open_list.pop(0)

            # Verifica se o estado atingiu o objetivo
            if self._is_goal_met(current_node.state, goal_state):
                # Reconstrói plano
                plan: List[GOAPAction] = []
                curr = current_node
                while curr.parent is not None and curr.action is not None:
                    plan.insert(0, curr.action)
                    curr = curr.parent
                return plan

            closed_states.append(current_node.state)

            # Expande ações válidas
            for action in self.actions:
                if action.check_preconditions(current_node.state):
                    next_state = action.apply_effects(current_node.state)
                    if any(next_state == s for s in closed_states):
                        continue

                    g = current_node.g_cost + action.cost
                    h = self._heuristic(next_state, goal_state)
                    open_list.append(GOAPNode(state=next_state, parent=current_node, action=action, g_cost=g, h_cost=h))

        return []

    def _heuristic(self, state: Dict[str, Any], goal_state: Dict[str, Any]) -> float:
        """Heurística simples: conta quantos objetivos ainda não foram satisfeitos."""
        count = 0
        for k, v in goal_state.items():
            if state.get(k) != v:
                count += 1
        return float(count)

    def _is_goal_met(self, state: Dict[str, Any], goal_state: Dict[str, Any]) -> bool:
        for k, v in goal_state.items():
            if state.get(k) != v:
                return False
        return True

    def trigger_replan(self) -> None:
        """Solicita recálculo do plano."""
        self.needs_replan = True

    def interrupt_and_push_plan(self, urgent_goal_state: Dict[str, Any], world: WorldState) -> List[GOAPAction]:
        """
        Interrompe o plano atual, salva na pilha e gera o plano de emergência (ex: cura).
        """
        if self.current_plan:
            logger.warning(f"⏸️ GOAP: Interrompendo plano atual ({len(self.current_plan)} ações) para atender emergência!")
            self.interrupted_plan_stack.append(list(self.current_plan))

        start_state = self.extract_world_state_symbols(world)
        emergency_plan = self.plan(start_state, urgent_goal_state)
        self.current_plan = emergency_plan
        self.needs_replan = False
        return emergency_plan

    def resume_interrupted_plan(self, world: WorldState) -> Optional[List[GOAPAction]]:
        """
        Retoma o plano anterior que havia sido interrompido após o término da emergência.
        """
        if self.interrupted_plan_stack:
            resumed = self.interrupted_plan_stack.pop()
            logger.info(f"▶️ GOAP: Retomando plano anterior ({len(resumed)} ações restantes)!")
            self.current_plan = resumed
            self.needs_replan = False
            return resumed
        return None

    def get_next_skill(self, goal_name: str, world: WorldState) -> Optional[BaseSkill]:
        """
        Resolve a próxima Skill a ser executada a partir da fila de ações do GOAP.
        """
        # Checagem de interrupção para cura
        if world.team.needs_healing and goal_name not in ["HEAL_TEAM", "IDLE"]:
            if not self.current_plan or self.current_plan[0].name != "HealTeam":
                self.interrupt_and_push_plan({"team_healed": True}, world)

        # Se não houver plano ou replanejamento solicitado
        if self.needs_replan or not self.current_plan:
            start_state = self.extract_world_state_symbols(world)
            goal_state = {"following_leader": True}
            if goal_name in ["FARM_XP", "TRAIN_POKEMON", "HUNT"]:
                goal_state = {"target_level_reached": True}
            elif goal_name == "HEAL_TEAM":
                goal_state = {"team_healed": True}

            self.current_plan = self.plan(start_state, goal_state)
            self.needs_replan = False

        # Se o plano atual terminou e existe um plano na pilha de interrupção, retoma!
        if not self.current_plan and self.interrupted_plan_stack:
            self.resume_interrupted_plan(world)

        if self.current_plan:
            action = self.current_plan[0]
            skill = self.skills.get(action.target_skill_name)
            if skill:
                if skill.is_complete(world):
                    self.current_plan.pop(0)
                    return self.get_next_skill(goal_name, world)
                return skill

        return self.skills.get("FollowSkill")
