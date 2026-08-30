"""
Klayton Companion Agent - Agente Autônomo e Social
===================================================

Integra os 4 Pilares da Cognição e Presença Social:
1. Perception (O que está acontecendo no jogo e com o jogador?)
2. Cognition (O que isso significa? Estado de relacionamento, personalidade e atenção compartilhada)
3. Agency (O que eu quero fazer? Conciliação de metas compartilhadas e pessoais)
4. Interaction (Como me comunico com Felipe e me comporto de forma crível e cooperativa?)

Autor: Klayton Companion Agent
Data: 2026-08-30
"""

from typing import Dict, Any, Optional
from ..world.world_state import WorldState
from ..core.event_bus import EventBus
from ..cognition.personality import Personality
from ..cognition.relationship import RelationshipState
from ..cognition.shared_attention import SharedAttention
from ..cognition.intent_parser import IntentParser
from ..interaction.dialogue_manager import DialogueManager
from ..agent.goal_manager import CompanionGoalManager, PersonalGoal
from ..decision.goal_engine import Goal
from ..decision.goap_planner import GOAPPlanner
try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger("CompanionAgent")


class KlaytonCompanionAgent:
    """
    KlaytonCompanionAgent - O Companheiro de Jogo Autônomo e Social.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None, components: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.components = components or {}

        # 1. PERCEPTION & STATE
        self.world: WorldState = WorldState()
        self.event_bus: EventBus = EventBus()

        # 2. COGNITION & SOCIAL MODEL
        self.personality: Personality = Personality(
            independence=0.35,
            curiosity=0.70,
            risk_tolerance=0.40,
            helpfulness=0.85,
            persistence=0.65
        )
        self.relationship: RelationshipState = RelationshipState(leader_name="Felipe")
        self.shared_attention: SharedAttention = SharedAttention()
        self.intent_parser: IntentParser = IntentParser()

        # 3. AGENCY & GOALS
        self.goal_manager: CompanionGoalManager = CompanionGoalManager(primary_shared_goal=Goal.FOLLOW_PLAYER)
        self.planner: GOAPPlanner = GOAPPlanner()

        # 4. INTERACTION & DIALOGUE
        self.dialogue: DialogueManager = DialogueManager(use_tts=False)

        self.running: bool = True
        self.paused: bool = False

        logger.info(f"🤝 Klayton Companion Agent Ativo! Líder: {self.relationship.leader_name}")

    def listen_and_respond(self, user_speech: str) -> str:
        """
        Processa frases do usuário, atualiza a intenção, contextualiza a fala e gera resposta verbal.
        """
        logger.info(f"👂 Ouvido de {self.relationship.leader_name}: '{user_speech}'")

        # 1. Atualiza instrução e estado no relacionamento social
        self.relationship.set_instruction(user_speech)

        # 2. Resolução de Atenção Compartilhada ("Pega esse", "Olha aquele")
        target_ref = self.shared_attention.resolve_target(user_speech, self.world)
        if target_ref:
            logger.info(f"🎯 Atenção compartilhada resolvida para: {target_ref}")

        # 3. Interpretação de Intenção e definição de Goal compartilhado
        intent = self.intent_parser.parse(user_speech)
        new_shared_goal = intent.to_goal()
        self.goal_manager.shared_goal = new_shared_goal
        self.planner.trigger_replan()

        # 4. Resposta verbal do Companheiro
        if self.relationship.is_waiting_for_player:
            utterance = self.dialogue.express_decision("waiting_player")
        elif new_shared_goal == Goal.HEAL_TEAM:
            utterance = self.dialogue.express_decision("heal_needed")
        else:
            utterance = self.dialogue.express_decision("resume_follow")

        return utterance.text

    def step(self) -> None:
        """
        Ciclo Cognitivo Continuo do Agente Companheiro:
        Percebe -> Cognição Social -> Seleção de Metas -> Planejamento GOAP -> Execução de Skill -> Fala.
        """
        if self.paused or not self.running:
            return

        # 1. Perception Update
        self.world.update_timestamp()

        # 2. Cognition & Relationship Evaluation
        if self.world.team.needs_healing and not self.relationship.is_waiting_for_player:
            if self.world.agent.current_subgoal != "HEAL_TEAM":
                self.dialogue.express_decision("heal_needed")

        # 3. Agency & Goal Selection
        active_goal = self.goal_manager.select_active_goal(
            is_waiting=self.relationship.is_waiting_for_player,
            team_needs_heal=self.world.team.needs_healing
        )
        self.world.agent.current_goal = self.goal_manager.shared_goal.name
        self.world.agent.current_subgoal = active_goal.name

        # 4. Planning & Skill Execution
        skill = self.planner.get_next_skill(active_goal.name, self.world)
        if skill:
            self.world.agent.active_skill = skill.name
            result = skill.execute(self.world, self.components)
            if result.failed:
                self.planner.trigger_replan()
        else:
            self.world.agent.active_skill = None
