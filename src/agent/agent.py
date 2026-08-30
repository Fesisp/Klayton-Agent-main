"""
Klayton Agent 2.0 - Core Autonomous Multimodal Agent
=====================================================

O Agente Autônomo Principal que integra:
- Perception (Visão computacional, OCR, detectores)
- WorldState (Single source of truth)
- EventBus (Barramento pub/sub de eventos)
- Memory (Working, Episodic, Semantic)
- GoalEngine & GOAPPlanner (Raciocínio, priorização e REPLAN contínuo)
- Skill Execution (Habilidades modulares desacopladas)

Autor: Klayton Agent 2.0 Framework
Data: 2026-08-30
"""

import time
from typing import Dict, Any, Optional
from ..world.world_state import WorldState
from ..core.event_bus import EventBus, GoalChangedEvent
from ..memory.agent_memory import AgentMemory
from ..decision.goal_engine import GoalEngine, Goal
from ..decision.goap_planner import GOAPPlanner
from ..cognition.intent_parser import IntentParser
try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger("KlaytonAgent")


class KlaytonAgent:
    """
    KlaytonAgent 2.0 - Framework de Agente Autônomo Multimodal.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None, components: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.components = components or {}
        
        # 1. Estado do Mundo & Barramento de Eventos
        self.world: WorldState = WorldState()
        self.event_bus: EventBus = EventBus()
        
        # 2. Sistema de Memória
        self.memory: AgentMemory = AgentMemory(pokemon_db=self.components.get('pokemon_db'))
        
        # 3. Raciocínio & Planejamento
        initial_goal_str = self.config.get('bot', {}).get('primary_goal', 'PROGRESS_STORY')
        initial_goal = Goal.from_string(str(initial_goal_str))
        self.goal_engine: GoalEngine = GoalEngine(primary_goal=initial_goal, config=config)
        self.planner: GOAPPlanner = GOAPPlanner()
        self.intent_parser: IntentParser = IntentParser()

        self.running: bool = True
        self.paused: bool = False
        
        logger.info(f"🤖 KlaytonAgent 2.0 Inicializado com Objetivo: {self.goal_engine.primary_goal.name}")

    def execute_natural_command(self, text_command: str) -> Goal:
        """
        Recebe um comando em linguagem natural, interpreta a intenção e atualiza o Objetivo do agente.
        """
        logger.info(f"🗣️ Processando comando de voz/texto: '{text_command}'")
        intent = self.intent_parser.parse(text_command)
        new_goal = intent.to_goal()
        
        old_goal_name = self.goal_engine.primary_goal.name
        self.goal_engine.set_primary_goal(new_goal)
        self.planner.trigger_replan()
        
        # Publica evento de alteração de metas no barramento
        self.event_bus.publish(GoalChangedEvent(old_goal=old_goal_name, new_goal=new_goal.name))
        return new_goal

    def step(self) -> None:
        """
        Executa um único ciclo do agente (Percebe -> Atualiza Mundo -> Planeja -> Executa Skill -> REPLAN).
        """
        if self.paused or not self.running:
            return

        # 1. Atualização do WorldState (se componentes de percepção estiverem conectados)
        self.world.update_timestamp()

        # 2. Avaliação de Raciocínio (Goal Engine)
        context = {
            'team_needs_heal': self.world.team.needs_healing,
            'in_battle': self.world.battle.in_battle,
        }
        active_goal = self.goal_engine.evaluate_subgoal(context)
        self.world.agent.current_goal = self.goal_engine.primary_goal.name
        self.world.agent.current_subgoal = active_goal.name

        # 3. Obtenção da próxima Skill através do GOAP Planner
        skill = self.planner.get_next_skill(active_goal.name, self.world)

        # 4. Execução da Skill
        if skill:
            self.world.agent.active_skill = skill.name
            result = skill.execute(self.world, self.components)
            if result.failed:
                logger.warning(f"⚠️ Falha na execução da Skill {skill.name}. Solicitando REPLAN...")
                self.planner.trigger_replan()
        else:
            self.world.agent.active_skill = None
