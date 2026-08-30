"""
Hotkey Listener - Sistema de controle global por teclas de atalho

Permite mudar o comportamento do bot em tempo real sem precisar reiniciar.
Funciona mesmo quando a janela do jogo está em foco.
"""

from pynput import keyboard
from loguru import logger
from enum import Enum
import threading
import time


class HotkeyCommand(Enum):
    """Comandos disponíveis via hotkeys."""
    IDLE = "idle"
    MISSION = "mission"
    HUNTING = "hunting"
    FOLLOW = "follow"
    PAUSE = "pause"
    RESUME = "resume"
    STOP = "stop"


class HotkeyListener:
    def __init__(self, bot_controller, config=None):
        """
        Inicializa o listener de hotkeys globais.
        
        Args:
            bot_controller: Instância do BotController para enviar comandos
            config: Dicionário de configuração com mapeamento de teclas
        """
        self.bot = bot_controller
        self.cfg = config or {}
        self.controls_cfg = self.cfg.get('controls', {})
        
        # Carrega mapeamento de teclas do config
        self.hotkeys = {
            self.controls_cfg.get('idle_key', '<f1>'): HotkeyCommand.IDLE,
            self.controls_cfg.get('mission_key', '<f2>'): HotkeyCommand.MISSION,
            self.controls_cfg.get('hunting_key', '<f3>'): HotkeyCommand.HUNTING,
            self.controls_cfg.get('follow_key', '<f4>'): HotkeyCommand.FOLLOW,
            self.controls_cfg.get('pause_key', '<f5>'): HotkeyCommand.PAUSE,
            self.controls_cfg.get('resume_key', '<f6>'): HotkeyCommand.RESUME,
            self.controls_cfg.get('stop_key', '<f9>'): HotkeyCommand.STOP,
        }
        
        self.listener = None
        self.running = False
        self.paused = False
        
        logger.info("🎮 Hotkey Listener inicializado")
        self._print_hotkey_map()
    
    def _print_hotkey_map(self):
        """Imprime mapeamento de teclas no console."""
        logger.info("=" * 50)
        logger.info("🎮 CONTROLES DISPONÍVEIS:")
        logger.info("=" * 50)
        
        key_map = {
            HotkeyCommand.IDLE: "Estado Ocioso (para tudo)",
            HotkeyCommand.MISSION: "Estado Missão (segue Goto/Talk)",
            HotkeyCommand.HUNTING: "Estado Caça (procura alvos)",
            HotkeyCommand.FOLLOW: "Seguir Personagem",
            HotkeyCommand.PAUSE: "Pausar Bot",
            HotkeyCommand.RESUME: "Retomar Bot",
            HotkeyCommand.STOP: "Parar Bot Completamente",
        }
        
        for key, command in self.hotkeys.items():
            description = key_map.get(command, "Desconhecido")
            logger.info(f"  {key.upper():<8} → {description}")
        
        logger.info("=" * 50)
    
    def start(self):
        """Inicia o listener em uma thread separada."""
        if self.running:
            logger.warning("Hotkey listener já está rodando")
            return
        
        self.running = True
        
        # Cria listener com callbacks para cada combinação
        # pynput usa sintaxe <key> para teclas especiais
        hotkey_combinations = {}
        for key, command in self.hotkeys.items():
            hotkey_combinations[key] = lambda cmd=command: self._on_hotkey(cmd)
        
        # Inicia listener global
        try:
            self.listener = keyboard.GlobalHotKeys(hotkey_combinations)
            self.listener.start()
            logger.info("✅ Hotkey listener ativo! Pressione as teclas para controlar o bot.")
        except Exception as e:
            logger.error(f"Erro ao iniciar GlobalHotKeys: {e}")
            raise
    
    def stop(self):
        """Para o listener."""
        if not self.running:
            return
        
        self.running = False
        if self.listener:
            self.listener.stop()
        
        logger.info("Hotkey listener parado")
    
    def _on_hotkey(self, command):
        """
        Callback executado quando uma hotkey é pressionada.
        
        Args:
            command: HotkeyCommand correspondente à tecla
        """
        try:
            logger.info(f"🎮 Hotkey detectada: {command.value.upper()}")
            
            if command == HotkeyCommand.IDLE:
                self._set_idle()
            elif command == HotkeyCommand.MISSION:
                self._set_mission()
            elif command == HotkeyCommand.HUNTING:
                self._set_hunting()
            elif command == HotkeyCommand.FOLLOW:
                self._set_follow()
            elif command == HotkeyCommand.PAUSE:
                self._pause_bot()
            elif command == HotkeyCommand.RESUME:
                self._resume_bot()
            elif command == HotkeyCommand.STOP:
                self._stop_bot()
            
        except Exception as e:
            logger.error(f"Erro ao processar hotkey {command}: {e}")
    
    def _set_idle(self):
        """Muda para Objetivo IDLE."""
        from ..decision.goal_engine import Goal
        
        if hasattr(self.bot, 'goal_engine'):
            self.bot.goal_engine.set_primary_goal(Goal.IDLE)
            logger.info("⏸️ Objetivo alterado para IDLE (Ocioso)")
        elif hasattr(self.bot, 'behavior'):
            self.bot.behavior = Goal.IDLE
            logger.info("⏸️ Bot mudado para estado IDLE (Ocioso)")
        else:
            logger.error("BotController não possui controle de objetivos")
    
    def _set_mission(self):
        """Muda para Objetivo PROGRESS_STORY (Missão)."""
        from ..decision.goal_engine import Goal
        
        if hasattr(self.bot, 'goal_engine'):
            self.bot.goal_engine.set_primary_goal(Goal.PROGRESS_STORY)
            logger.info("🗺️ Objetivo alterado para PROGRESS_STORY (Missão)")
        elif hasattr(self.bot, 'behavior'):
            self.bot.behavior = Goal.PROGRESS_STORY
            logger.info("🗺️ Bot mudado para estado PROGRESS_STORY")
        else:
            logger.error("BotController não possui controle de objetivos")
    
    def _set_hunting(self):
        """Muda para Objetivo HUNT (Caça)."""
        from ..decision.goal_engine import Goal
        
        if hasattr(self.bot, 'goal_engine'):
            self.bot.goal_engine.set_primary_goal(Goal.HUNT)
            targets = getattr(self.bot, 'hunt_target_pokemon', [])
            logger.info("🎣 Objetivo alterado para HUNT (Caça)")
            logger.info(f"   → Alvos: {targets if targets else 'Nenhum configurado'}")
        elif hasattr(self.bot, 'behavior'):
            self.bot.behavior = Goal.HUNT
            logger.info("🎣 Bot mudado para estado HUNT")
        else:
            logger.error("BotController não possui controle de objetivos")
    
    def _set_follow(self):
        """Muda para Objetivo FOLLOW_PLAYER (Seguir)."""
        from ..decision.goal_engine import Goal
        
        if hasattr(self.bot, 'goal_engine'):
            self.bot.goal_engine.set_primary_goal(Goal.FOLLOW_PLAYER)
            logger.info("👤 Objetivo alterado para FOLLOW_PLAYER (Seguir)")
        elif hasattr(self.bot, 'behavior'):
            self.bot.behavior = Goal.FOLLOW_PLAYER
            logger.info("👤 Bot mudado para estado FOLLOW_PLAYER")
        else:
            logger.error("BotController não possui controle de objetivos")
    
    def _pause_bot(self):
        """Pausa o bot temporariamente."""
        if hasattr(self.bot, 'paused'):
            self.bot.paused = True
            logger.info("⏸️ Bot PAUSADO")
            logger.info("   → Pressione F6 para retomar")
        else:
            logger.error("BotController não tem atributo 'paused'")
    
    def _resume_bot(self):
        """Retoma o bot após pausa."""
        if hasattr(self.bot, 'paused'):
            self.bot.paused = False
            logger.info("▶️ Bot RETOMADO")
        else:
            logger.error("BotController não tem atributo 'paused'")
    
    def _stop_bot(self):
        """Para o bot completamente."""
        if hasattr(self.bot, 'running'):
            self.bot.running = False
            logger.info("🛑 Bot PARADO completamente")
            logger.info("   → Reinicie o script para usar novamente")
        else:
            logger.error("BotController não tem atributo 'running'")
    
    def is_paused(self):
        """Verifica se o bot está pausado."""
        return getattr(self.bot, 'paused', False)


class HotkeyManager:
    """Gerenciador simplificado para integração fácil."""
    
    @staticmethod
    def create_and_start(bot_controller, config):
        """
        Cria e inicia o hotkey listener.
        
        Args:
            bot_controller: Instância do BotController
            config: Configuração do bot
            
        Returns:
            HotkeyListener: Instância do listener
        """
        listener = HotkeyListener(bot_controller, config)
        listener.start()
        return listener
