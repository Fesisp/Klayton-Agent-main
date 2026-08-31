"""
Battle Outcome Verifier - Validador Empírico de Resultados de Ação de Combate
=============================================================================

Avalia as observações e eventos empíricos pós-ação para confirmar ou rejeitar
o efeito no jogo. Nenhuma ação é considerada concluída sem evidência observada.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional
from .battle_action import BattleAction, BattleActionType
from .battle_observation import BattleObservation
from .battle_event import BattleEvent, BattleEventType


class OutcomeStatus(Enum):
    """Status de verificação de resultado de ação."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"
    TIMEOUT = "timeout"
    AMBIGUOUS = "ambiguous"


@dataclass
class ActionOutcome:
    """Resultado da verificação empírica de uma ação."""
    status: OutcomeStatus
    confidence: float
    evidence: List[str] = field(default_factory=list)


class BattleOutcomeVerifier:
    """Validador de resultados de ações de combate."""

    def __init__(self, timeout_seconds: float = 8.0):
        self.timeout_seconds = timeout_seconds

    def verify(
        self,
        action: BattleAction,
        before: Optional[BattleObservation],
        after_observations: List[BattleObservation],
        events: List[BattleEvent]
    ) -> ActionOutcome:
        """
        Verifica se a ação enviada gerou efeito observável no ambiente do jogo.
        """
        if before is None or not after_observations:
            return ActionOutcome(
                status=OutcomeStatus.PENDING,
                confidence=0.0,
                evidence=["Aguardando observações pós-ação"]
            )

        latest = after_observations[-1]
        elapsed = latest.timestamp - before.timestamp if latest.timestamp and before.timestamp else 0.0

        evidence: List[str] = []

        # 1. Verificação para Ação MOVE (Ataque)
        if action.type == BattleActionType.MOVE:
            # Evidência 1: Variação de HP do adversário
            hp_events = [e for e in events if e.type == BattleEventType.ENEMY_HP_CHANGED]
            if hp_events:
                evidence.append(f"HP do adversário alterado: {hp_events[0].data.get('delta')}")
                return ActionOutcome(status=OutcomeStatus.CONFIRMED, confidence=0.95, evidence=evidence)

            # Evidência 2: Mudança de status do adversário
            status_events = [e for e in events if e.type == BattleEventType.ENEMY_STATUS_CHANGED]
            if status_events:
                evidence.append(f"Status do adversário alterado para {status_events[0].data.get('after')}")
                return ActionOutcome(status=OutcomeStatus.CONFIRMED, confidence=0.95, evidence=evidence)

            # Evidência 3: Faint do adversário ou vitória/término da batalha
            if any(e.type in [BattleEventType.ENEMY_FAINTED, BattleEventType.BATTLE_WON, BattleEventType.BATTLE_ENDED] for e in events):
                evidence.append("Adversário derrotado após o ataque (batalha encerrada)")
                return ActionOutcome(status=OutcomeStatus.CONFIRMED, confidence=0.98, evidence=evidence)

            # Evidência 4: Transição de turno observada com reabertura do menu
            if any(e.type == BattleEventType.TURN_STARTED for e in events):
                evidence.append("Novo turno iniciado após execução do ataque")
                return ActionOutcome(status=OutcomeStatus.CONFIRMED, confidence=0.90, evidence=evidence)

        # 2. Verificação para Ação SWITCH (Troca)
        elif action.type == BattleActionType.SWITCH:
            switch_events = [e for e in events if e.type == BattleEventType.PLAYER_SWITCHED]
            if switch_events:
                new_pkmn = switch_events[0].data.get("after")
                evidence.append(f"Pokémon ativo alterado para {new_pkmn}")
                if action.switch_target and new_pkmn and action.switch_target.lower() not in new_pkmn.lower():
                    evidence.append(f"AVISO: Trocou para {new_pkmn}, mas alvo esperado era {action.switch_target}")
                    return ActionOutcome(status=OutcomeStatus.AMBIGUOUS, confidence=0.70, evidence=evidence)
                return ActionOutcome(status=OutcomeStatus.CONFIRMED, confidence=0.95, evidence=evidence)

            if before.player_pokemon and latest.player_pokemon and before.player_pokemon.lower() != latest.player_pokemon.lower():
                evidence.append(f"Pokémon ativo alterado de {before.player_pokemon} para {latest.player_pokemon}")
                return ActionOutcome(status=OutcomeStatus.CONFIRMED, confidence=0.95, evidence=evidence)

        # 3. Verificação para Ação RUN (Fuga)
        elif action.type == BattleActionType.RUN:
            if before.in_battle and not latest.in_battle:
                evidence.append("Combate encerrado com sucesso após tentativa de fuga")
                return ActionOutcome(status=OutcomeStatus.CONFIRMED, confidence=0.98, evidence=evidence)

        # 4. Verificação para Ação CAPTURE (Captura)
        elif action.type == BattleActionType.CAPTURE:
            if any(e.type == BattleEventType.CAPTURE_SUCCEEDED for e in events):
                evidence.append("Captura confirmada com sucesso")
                return ActionOutcome(status=OutcomeStatus.CONFIRMED, confidence=0.99, evidence=evidence)
            if any(e.type == BattleEventType.CAPTURE_FAILED for e in events):
                evidence.append("Captura falhou (Pokébola balançou)")
                return ActionOutcome(status=OutcomeStatus.REJECTED, confidence=0.95, evidence=evidence)

        # Timeout Check
        if elapsed >= self.timeout_seconds:
            return ActionOutcome(
                status=OutcomeStatus.TIMEOUT,
                confidence=0.0,
                evidence=[f"Nenhum efeito observável dentro do limite de {self.timeout_seconds}s"]
            )

        return ActionOutcome(
            status=OutcomeStatus.PENDING,
            confidence=0.0,
            evidence=["Aguardando evidências observáveis no ambiente"]
        )
