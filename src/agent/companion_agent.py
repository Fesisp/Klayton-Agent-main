"""
KlaytonCompanionAgent - Cérebro Central Unificado do Companion Agent 2.0
========================================================================

Integração Completa:
1. WorldState como Fonte Única da Verdade (Totalmente Alimentado a Cada Ciclo)
2. GoalInstance Parametrizado (Target, Target Level, Restrições)
3. Seleção de Metas via Utility AI (utility = reward - risk - cost - time)
4. GOAPPlanner (Planejador de Sequência Estratégica A*) + HierarchicalPlanner
5. Tríade Mestra (NavigationSystem + RecoveryManager + Skills)
6. VoiceListener (Microfone ao Vivo Ativado) + TTS (Sintetizador de Voz Nativo Ativado)
7. Memória Tríplice Persistente (Working, Episodic, Semantic) Ativamente Consultada

Autor: Klayton Companion Agent Framework
Data: 2026-08-30
"""

import time
from typing import Dict, Any, Optional
from pathlib import Path

from ..platform.audio_alerts import AudioAlertService

from ..world.world_state import WorldState, Observation
from ..decision.goal_engine import Goal, GoalInstance
from ..decision.goap_planner import GOAPPlanner
from ..decision.utility_engine import UtilityEngine
from .goal_manager import CompanionGoalManager, PersonalGoal
from ..cognition.relationship import RelationshipState
from ..cognition.shared_attention import SharedAttention
from ..cognition.intent_parser import IntentParser
from ..cognition.memory_system import MemorySystem
from ..world.quest_engine import QuestEngine
from ..interaction.dialogue_manager import DialogueManager
from ..interaction.voice_listener import VoiceListener
from ..skills.base_skill import SkillStatus
from ..perception.perception_snapshot import PerceptionSnapshot
from ..perception.game_state_detector import GameState
from ..perception.chat_handler import ChatHandler
from ..utils.notifier import NotificationManager

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger("KlaytonCompanionAgent")


class KlaytonCompanionAgent:
    """
    Agente Companheiro Autônomo de Elite do Klayton 2.0.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None, components: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.components = components or {}
        self.notifier: NotificationManager = NotificationManager(self.config)

        # 0. PERCEPTION MANAGER (Desacoplado)
        from ..perception.perception_manager import PerceptionManager
        self.perception: PerceptionManager = self.components.get('perception') or PerceptionManager(self.config, self.components)

        # 1. WORLD STATE (SINGLE SOURCE OF TRUTH)
        self.world: WorldState = WorldState()

        # 2. COGNITION, PERSONALITY & MEMORY
        self.relationship: RelationshipState = RelationshipState(leader_name="Felipe")
        self.shared_attention: SharedAttention = SharedAttention()
        self.intent_parser: IntentParser = IntentParser()
        self.memory: MemorySystem = MemorySystem()
        self.quest_engine: QuestEngine = QuestEngine()

        # 3. AGENCY & GOALS (Utility AI & GoalInstance)
        initial_goal_str = self.config.get('bot', {}).get('primary_goal', 'FOLLOW_PLAYER')
        self.goal_manager: CompanionGoalManager = CompanionGoalManager(
            primary_shared_goal=Goal.from_string(initial_goal_str)
        )
        self.planner: GOAPPlanner = GOAPPlanner()

        from .nav_recovery_engine import NavRecoverySkillEngine
        self.master_triad: NavRecoverySkillEngine = NavRecoverySkillEngine()

        # 4. INTERACTION & DIALOGUE (TTS ATIVADO & LIVE VOICE LISTENING)
        self.dialogue: DialogueManager = DialogueManager(use_tts=True)
        self.voice_listener: VoiceListener = VoiceListener(
            agent_callback=self.listen_and_respond,
            dialogue_manager=self.dialogue
        )

        # 5. SECURITY & STEALTH
        from ..security.stealth_engine import ProcessStealthEngine, AntiAttachWatchdog
        ProcessStealthEngine.apply_stealth_protection()
        self.stealth_watchdog: AntiAttachWatchdog = AntiAttachWatchdog()
        self.stealth_watchdog.start()

        self.audio_alerts: AudioAlertService = AudioAlertService()

        # Controle de Execução
        self.running: bool = True
        self.paused: bool = False
        self.debug: bool = bool(self.config.get('bot', {}).get('debug_mode', False))
        self.chat_handler: Optional[ChatHandler] = None

        logger.info(f"🤝 Klayton Companion Agent Inicializado! Líder: {self.relationship.leader_name} | TTS: ON | Live Voice: Ready")

    @property
    def behavior(self) -> Goal:
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
        Processa comandos de voz com preservação de alvos (ex: "Pikachu", lvl 35),
        registra na memória episódica e responde verbalmente via TTS.
        """
        logger.info(f"🎙️ Ouvindo comando do líder: '{user_speech}'")
        self.memory.remember(category="dialogue", content=f"Felipe disse: {user_speech}", importance=0.8)

        # Trata termos dêiticos (ex: "pega esse bicho")
        resolved_target = self.shared_attention.resolve_target(user_speech, self.world)
        
        # Atualiza o contexto social do RelationshipState
        self.relationship.set_instruction(user_speech)
        
        # Converte em intenção estruturada e GoalInstance parametrizada
        intent = self.intent_parser.parse(user_speech)
        if resolved_target and not intent.target:
            intent.target = resolved_target

        goal_instance = intent.to_goal_instance()
        # Ordens diretas do usuário possuem prioridade máxima (2.0) sobre utilidades passivas!
        goal_instance.priority = 2.0
        self.goal_manager.set_shared_goal_instance(goal_instance)

        if intent.target:
            self.goal_manager.add_personal_goal(PersonalGoal(
                name=f"train_{intent.target}",
                target=intent.target,
                desired_value=intent.constraints.get("target_level", 35)
            ))
            logger.info(f"🎯 Objetivo Parametrizado Ativado: Treinar {intent.target} até nível {intent.constraints.get('target_level', 35)}")

        # Resposta verbal do diálogo
        if goal_instance.type == Goal.FOLLOW_PLAYER:
            utterance = self.dialogue.express_decision("resume_follow")
        elif goal_instance.type == Goal.HEAL_TEAM:
            utterance = self.dialogue.express_decision("heal_needed")
        else:
            utterance = self.dialogue.express_decision("waiting_player")

        return utterance.text

    def step(self) -> None:
        """
        Ciclo Cognitivo Contínuo do Agente Companheiro:
        Alimenta WorldState ➔ Reflexão de Memória ➔ Seleção de GoalInstance por Utility AI ➔ Injeção de Parâmetros na Skill.
        """
        if self.paused or not self.running:
            return

        # 1. Update Timestamps & Context
        self.world.update_timestamp()

        # 2. Reflexão da Memória Contextual (Recall estatístico para apoio de decisão)
        decision_context = self.memory.recall_for_decision(self.world, self.goal_manager.shared_goal_instance)
        best_spot = decision_context.get("best_known_spot")
        if best_spot and self.world.location.current_map in ["Unknown", ""]:
            self.world.location.current_map = best_spot

        # 3. Agency & Goal Selection (Decidido pela UtilityEngine: retorna GoalInstance com target/target_level/location)
        active_goal_instance = self.goal_manager.select_active_goal(
            is_waiting=self.relationship.is_waiting_for_player,
            team_needs_heal=self.world.team.needs_healing,
            world=self.world
        )

        # Se houver rota aprendida na memória e o objetivo envolve treino/farm, injeta o local na GoalInstance!
        if best_spot and active_goal_instance.type in [Goal.FARM_XP, Goal.TRAIN_POKEMON, Goal.HUNT]:
            active_goal_instance.location_hint = best_spot
        self.world.agent.current_goal = self.goal_manager.shared_goal.name
        self.world.agent.current_subgoal = active_goal_instance.name

        # 4. Master Triad Execution (GOAP + Skill Parameter Injection + Recovery)
        result = self.master_triad.execute_step(active_goal_instance, self.world, self.components)
        if result.failed or result.status == SkillStatus.INTERRUPTED:
            self.planner.trigger_replan()

    def run(self) -> None:
        """
        Loop Principal do Runtime do Klayton Companion Agent.
        Inicia a escuta de voz ao vivo, alimenta continuamente TODOS os ramos do WorldState via PerceptionSnapshot,
        e dispara a agência autônoma.
        """
        logger.info("==========================================================")
        logger.info("🤝 KlaytonCompanionAgent started (Cérebro Central do Runtime)")
        logger.info("🌐 WorldState active (Single Source of Truth)")
        logger.info("👁️ Full Multi-Branch Perception active")
        logger.info("🎯 CompanionGoalManager & UtilityEngine active")
        logger.info("🎙️ Live Voice Listening & Anti-Self-Hearing ACTIVE")
        logger.info("🗣️ Native Text-To-Speech (TTS) ACTIVE")
        logger.info("⚡ GOAP & Master Triad Skill Engine active")
        logger.info("🛡️ Watchdog & Recovery System active")
        logger.info("==========================================================")

        # 1. Ativa a escuta de voz ao vivo (Live Voice Listener)
        try:
            self.voice_listener.start_live_listening()
            logger.info("🎤 Escuta de voz contínua ativada no microfone principal!")
        except Exception as e:
            logger.warning(f"⚠️ Não foi possível iniciar o microfone ao vivo (modo texto ativado): {e}")

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

                # 2. Captura de Snapshot de Percepção Desacoplada
                snapshot = self.perception.capture_snapshot()

                # 3. Detecção de PM (Mensagem Privada de Segurança)
                if self.perception.check_pm_alert(self.perception.capture_frame()):
                    logger.critical("🚨 PAUSANDO KLAYTON POR SEGURANÇA (PM RECEBIDA)!")
                    self.paused = True
                    self.notifier.notify_all("⚠️ MENSAGEM PRIVADA RECEBIDA! O agente foi pausado imediatamente para evitar ban.", is_critical=True)
                    for _ in range(3):
                        self.audio_alerts.warning()
                        time.sleep(0.3)
                    continue

                if snapshot.game_state == "SHINY_FOUND":
                    logger.critical("✨ SHINY ENCONTRADO! PAUSANDO AGENTE!")
                    self.paused = True
                    self.notifier.notify_shiny_found("Shiny Pokemon", self.world.location.current_map)
                    continue

                # 4. Alimentação Integral do WorldState via PerceptionSnapshot
                self.world.apply_snapshot(snapshot)

                # 5. Executa o Ciclo Cognitivo de Tomada de Decisão
                self.step()

                if self.debug:
                    logger.debug(f"GameState: {snapshot.game_state} | Active Goal: {self.world.agent.current_goal} | Subgoal: {self.world.agent.current_subgoal}")

                time.sleep(loop_interval)

            except KeyboardInterrupt:
                logger.info("🛑 Interrupção manual (Ctrl+C). Encerrando Klayton Companion Agent...")
                self.running = False
                break
            except Exception as e:
                logger.exception(f"Erro no loop do KlaytonCompanionAgent: {e}")
                time.sleep(2.0)
