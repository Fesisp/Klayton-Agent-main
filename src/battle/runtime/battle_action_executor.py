"""
Battle Action Executor - Executor Físico de Ações de Combate
============================================================

Traduz uma BattleAction abstrata em sequência de comandos físicos protegida contra cliques duplicados (input_committed lock).

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, Optional
from .battle_action import BattleAction, BattleActionType
from .battle_observation import BattleObservation


class ExecutorPhase(Enum):
    """Fases da máquina de estados do executor físico."""
    IDLE = "idle"
    OPENING_MENU = "opening_menu"
    SELECTING_OPTION = "selecting_option"
    CONFIRMING = "confirming"
    WAITING_RESULT = "waiting_result"
    DONE = "done"
    FAILED = "failed"


class BattleActionExecutor:
    """Executa ações físicas de combate no jogo sem enviar cliques duplicados."""

    def __init__(self):
        self.phase: ExecutorPhase = ExecutorPhase.IDLE
        self.current_action: Optional[BattleAction] = None
        self.input_committed: bool = False

    def start(self, action: BattleAction, observation: Optional[BattleObservation] = None) -> None:
        """Inicializa o executor para uma nova ação."""
        self.current_action = action
        self.phase = ExecutorPhase.OPENING_MENU
        self.input_committed = False

    def tick(self, observation: Optional[BattleObservation], input_simulator: Any, screen: Any = None) -> ExecutorPhase:
        """Executa um passo da máquina de estados física."""
        if not self.current_action or self.phase == ExecutorPhase.DONE:
            return ExecutorPhase.DONE

        if self.phase == ExecutorPhase.FAILED:
            return ExecutorPhase.FAILED

        # Se o input físico já foi enviado, aguarda o resultado sem enviar cliques duplicados
        if self.input_committed:
            self.phase = ExecutorPhase.WAITING_RESULT
            return self.phase

        action = self.current_action

        try:
            if action.type == BattleActionType.MOVE:
                slot = action.move_slot if action.move_slot is not None else 0
                if hasattr(input_simulator, 'humanized_click_in_slot'):
                    input_simulator.humanized_click_in_slot(slot)
                elif hasattr(input_simulator, 'click_in_slot'):
                    input_simulator.click_in_slot(slot)
                elif hasattr(input_simulator, 'press'):
                    input_simulator.press(str(slot + 1))
                self.input_committed = True
                self.phase = ExecutorPhase.WAITING_RESULT

            elif action.type == BattleActionType.SWITCH:
                if hasattr(input_simulator, 'click_pokemon_button') and screen:
                    img = screen.capture() if hasattr(screen, 'capture') else None
                    input_simulator.click_pokemon_button(img)
                elif hasattr(input_simulator, 'press'):
                    input_simulator.press('p')
                self.input_committed = True
                self.phase = ExecutorPhase.WAITING_RESULT

            elif action.type == BattleActionType.RUN:
                if hasattr(input_simulator, 'click_run_button') and screen:
                    img = screen.capture() if hasattr(screen, 'capture') else None
                    input_simulator.click_run_button(img)
                elif hasattr(input_simulator, 'press'):
                    input_simulator.press('r')
                self.input_committed = True
                self.phase = ExecutorPhase.WAITING_RESULT

            elif action.type in [BattleActionType.ITEM, BattleActionType.CAPTURE]:
                if hasattr(input_simulator, 'click_bag_button') and screen:
                    img = screen.capture() if hasattr(screen, 'capture') else None
                    input_simulator.click_bag_button(img)
                elif hasattr(input_simulator, 'press'):
                    input_simulator.press('b')
                self.input_committed = True
                self.phase = ExecutorPhase.WAITING_RESULT

        except Exception:
            self.phase = ExecutorPhase.FAILED
            return self.phase

        return self.phase

    def reset(self) -> None:
        """Reseta o estado interno do executor."""
        self.phase = ExecutorPhase.IDLE
        self.current_action = None
        self.input_committed = False
