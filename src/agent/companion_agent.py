"""
Klayton Companion Agent - Agente Autônomo e Social (Cérebro Central do Runtime)
================================================================================

Integra os 4 Pilares da Cognição e Presença Social:
1. Perception (O que está acontecendo no jogo e com o jogador?)
2. Cognition (O que isso significa? Estado de relacionamento, personalidade e atenção compartilhada)
3. Agency (O que eu quero fazer? Conciliação de metas compartilhadas e pessoais)
4. Interaction (Como me comunico com Felipe e me comporto de forma crível e cooperativa?)

Substitui definitivamente o BotController legado como executor primário do runtime no PokeOne.

Autor: Klayton Companion Agent Framework
Data: 2026-08-30
"""

import time
import winsound
from typing import Dict, Any, Optional
from ..world.world_state import WorldState, Observation
from ..core.event_bus import EventBus
from ..cognition.personality import Personality
from ..cognition.relationship import RelationshipState
from ..cognition.shared_attention import SharedAttention
from ..cognition.intent_parser import IntentParser
from ..interaction.dialogue_manager import DialogueManager
from ..agent.goal_manager import CompanionGoalManager, PersonalGoal
from ..decision.goal_engine import Goal
from ..decision.goap_planner import GOAPPlanner
from ..skills.base_skill import SkillStatus
from ..perception.game_state_detector import GameState
from ..perception.chat_handler import ChatHandler
from ..utils.notifier import NotificationManager
from ..utils.window_handler import WindowHandler
try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger("CompanionAgent")


class KlaytonCompanionAgent:
    """
    KlaytonCompanionAgent - O Companheiro de Jogo Autônomo, Social e Central do Runtime.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None, components: Optional[Dict[str, Any]] = None):
        self.config: Dict[str, Any] = config or {}
        self.components: Dict[str, Any] = components or {}

        # 1. PERCEPTION & STATE
        self.world: WorldState = WorldState()
        self.event_bus: EventBus = EventBus()
        self.win_handler: WindowHandler = WindowHandler(window_title=self.config.get('screen', {}).get('window_title', 'PokeOne'))
        self.notifier: NotificationManager = NotificationManager(self.config)

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
        from ..cognition.memory_system import MemorySystem
        from ..world.quest_engine import QuestEngine
        self.memory: MemorySystem = MemorySystem()
        self.quest_engine: QuestEngine = QuestEngine()

        # 3. AGENCY & GOALS
        initial_goal_str = self.config.get('bot', {}).get('primary_goal', 'FOLLOW_PLAYER')
        self.goal_manager: CompanionGoalManager = CompanionGoalManager(
            primary_shared_goal=Goal.from_string(initial_goal_str)
        )
        self.planner: GOAPPlanner = GOAPPlanner()
        from .nav_recovery_engine import NavRecoverySkillEngine
        self.master_triad: NavRecoverySkillEngine = NavRecoverySkillEngine()

        # 4. INTERACTION & DIALOGUE
        self.dialogue: DialogueManager = DialogueManager(use_tts=False)
        from ..interaction.voice_listener import VoiceListener
        self.voice_listener: VoiceListener = VoiceListener(
            agent_callback=self.listen_and_respond,
            dialogue_manager=self.dialogue
        )

        # 5. SECURITY & STEALTH (PROJETO INTERVIEW)
        from ..security.stealth_engine import ProcessStealthEngine, AntiAttachWatchdog
        ProcessStealthEngine.apply_stealth_protection()
        self.stealth_watchdog: AntiAttachWatchdog = AntiAttachWatchdog()
        self.stealth_watchdog.start()

        # Controle de Execução
        self.running: bool = True
        self.paused: bool = False
        self.debug: bool = bool(self.config.get('bot', {}).get('debug_mode', False))
        self.chat_handler: Optional[ChatHandler] = None

        logger.info(f"🤝 Klayton Companion Agent Inicializado! Líder: {self.relationship.leader_name}")

    @property
    def behavior(self) -> Goal:
        """Compatibilidade para HotkeyManager e listeners externos."""
        return self.goal_manager.shared_goal

    @behavior.setter
    def behavior(self, val: Any) -> None:
        if isinstance(val, Goal):
            self.goal_manager.shared_goal = val
        else:
            self.goal_manager.shared_goal = Goal.from_string(str(val))
        self.planner.trigger_replan()
        logger.info(f"🎯 Meta Compartilhada Atualizada para: {self.goal_manager.shared_goal.name}")

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
        Ciclo Cognitivo Continuo do Agente Companheiro (via Tríade Mestra):
        Percebe -> Cognição Social -> Seleção de Metas -> Execution Engine (Nav + Recovery + Skills) -> Fala.
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

        # 4. Master Triad Execution (Navigation + Recovery + Skills)
        result = self.master_triad.execute_step(active_goal.name, self.world, self.components)
        if result.failed or result.status == SkillStatus.INTERRUPTED:
            self.planner.trigger_replan()

    def run(self) -> None:
        """
        Loop Principal do Runtime do Klayton Companion Agent.
        Executa a percepção de quadros, alimenta o WorldState como Fonte Única da Verdade,
        e dispara o ciclo autônomo do agente.
        """
        logger.info("==========================================================")
        logger.info("🤝 KlaytonCompanionAgent started (Cérebro Central do Runtime)")
        logger.info("🌐 WorldState active (Single Source of Truth)")
        logger.info("👁️ Perception active")
        logger.info("🎯 CompanionGoalManager active")
        logger.info("🎙️ Voice Listener & Anti-Self-Hearing active")
        logger.info("⚡ Skill Engine active (GOAP & Utility AI)")
        logger.info("🛡️ Watchdog & Recovery System active")
        logger.info("==========================================================")

        screen = self.components.get('screen')
        detector = self.components.get('detector')

        if detector and not self.chat_handler:
            self.chat_handler = ChatHandler(detector, self.config)

        loop_interval = float(self.config.get('bot', {}).get('loop_interval', 0.5))

        while self.running:
            try:
                if self.paused:
                    time.sleep(0.3)
                    continue

                # 1. Captura de Frame
                img = screen.capture() if (screen and hasattr(screen, 'capture')) else None

                # 2. Detecção de PM (Mensagem Privada de Segurança)
                if img is not None and self.chat_handler and self.chat_handler.check_for_alerts(img):
                    logger.critical("🚨 PAUSANDO KLAYTON POR SEGURANÇA (PM RECEBIDA)!")
                    self.paused = True
                    self.notifier.notify_all("⚠️ MENSAGEM PRIVADA RECEBIDA! O agente foi pausado imediatamente para evitar ban.", is_critical=True)
                    for _ in range(3):
                        winsound.MessageBeep(winsound.MB_ICONHAND)
                        time.sleep(0.3)
                    continue

                # 3. Percepção Visual e Atualização do WorldState (Single Source of Truth)
                game_state = GameState.EXPLORING
                if detector and hasattr(detector, 'detect_state') and img is not None:
                    game_state = detector.detect_state(img)

                # Prioridade máxima: Shiny detectado
                if game_state == GameState.SHINY_FOUND:
                    logger.critical("✨ SHINY ENCONTRADO! PAUSANDO AGENTE!")
                    self.paused = True
                    self.notifier.notify_shiny_found("Shiny Pokemon", self.world.location.current_map)
                    continue

                # Aplica observação ao WorldState com validação de confiança
                obs = Observation(
                    category="battle",
                    data={
                        "in_battle": (game_state == GameState.IN_BATTLE),
                        "is_shiny": (game_state == GameState.SHINY_FOUND)
                    },
                    confidence=0.95
                )
                self.world.apply_observation(obs)

                # 4. Executa o ciclo cognitivo e comanda as Skills
                self.step()

                if self.debug:
                    logger.debug(f"GameState: {game_state.name} | Active Goal: {self.world.agent.current_goal} | Subgoal: {self.world.agent.current_subgoal}")

                time.sleep(loop_interval)

            except KeyboardInterrupt:
                logger.info("🛑 Interrupção manual (Ctrl+C). Encerrando Klayton Companion Agent...")
                self.running = False
                break
            except Exception as e:
                logger.exception(f"Erro no loop do KlaytonCompanionAgent: {e}")
                time.sleep(2.0)
