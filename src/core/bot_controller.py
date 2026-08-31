"""
BotController (Legacy Compatibility Adapter)
============================================

Fornece uma camada de compatibilidade retroativa para scripts legados,
delegando 100% da percepção, cognição e execução ao KlaytonCompanionAgent.

Autor: Klayton Companion Agent Framework
Data: 2026-08-30
"""

from typing import Dict, Any, Optional
from ..agent.companion_agent import KlaytonCompanionAgent
from ..decision.goal_engine import Goal

# Alias para retrocompatibilidade
BotBehavior = Goal


class BotController:
    """
    Adaptador de compatibilidade legado que delega para o KlaytonCompanionAgent.
    """

    def __init__(self, config: Dict[str, Any], components: Dict[str, Any]):
        self.cfg = config
        self.components = components
        self.cap = components.get('screen')
        self.detector = components.get('detector')
        self.input = components.get('input')
        self.strategy = components.get('strategy')
        self.ocr = components.get('ocr')
        self.team_mgr = components.get('team_mgr')

        # Cria o agente de verdade
        self.companion_agent = KlaytonCompanionAgent(config=config, components=components)

    @property
    def running(self) -> bool:
        return self.companion_agent.running

    @running.setter
    def running(self, val: bool) -> None:
        self.companion_agent.running = val

    @property
    def paused(self) -> bool:
        return self.companion_agent.paused

    @paused.setter
    def paused(self, val: bool) -> None:
        self.companion_agent.paused = val

    @property
    def behavior(self) -> Goal:
        return self.companion_agent.behavior

    @behavior.setter
    def behavior(self, val: Any) -> None:
        self.companion_agent.behavior = val

    def run(self) -> None:
        """Delega a execução diretamente ao loop nativo do KlaytonCompanionAgent."""
        self.companion_agent.run()

    # Métodos legados de conveniência que chamam a Tríade Mestra
    def handle_shiny(self, img=None) -> None:
        self.companion_agent.paused = True

    def handle_battle(self, img=None) -> None:
        self.companion_agent.step()

    def handle_hunting(self, img=None) -> None:
        self.companion_agent.step()

    def handle_mission(self, img=None) -> None:
        self.companion_agent.step()

    def _recovery_search(self) -> None:
        self.companion_agent.master_triad.recovery_mgr.handle_failure("Manual legacy recovery trigger", self.companion_agent.world, self.components)