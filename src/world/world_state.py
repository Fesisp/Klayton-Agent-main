"""
World State - Fonte Única da Verdade do Agente
==============================================

Representa o modelo completo e unificado do mundo, agregando todas as observações
da visão computacional, OCR, detecção de estado, mapa, time e ambiente.

Autor: Klayton Agent 2.0 Framework
Data: 2026-08-30
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
import time


@dataclass
class PokemonInfo:
    """Informações de um Pokémon da equipe ou inimigo."""
    name: str = "Unknown"
    level: int = 1
    hp_percentage: float = 1.0  # 0.0 a 1.0
    max_hp: int = 100
    current_hp: int = 100
    status: str = "OK"  # OK, Poison, Burn, Sleep, Freeze, Paralyze
    moves: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class PlayerState:
    """Estado do personagem do jogador."""
    name: Optional[str] = None
    position: Optional[Tuple[int, int]] = None
    map_name: str = "Unknown"
    in_water: bool = False
    money: int = 0


@dataclass
class TeamState:
    """Estado do time do jogador."""
    members: List[PokemonInfo] = field(default_factory=list)
    active_index: int = 0

    @property
    def active_pokemon(self) -> Optional[PokemonInfo]:
        if 0 <= self.active_index < len(self.members):
            return self.members[self.active_index]
        return None

    @property
    def average_hp_percentage(self) -> float:
        if not self.members:
            return 1.0
        return sum(p.hp_percentage for p in self.members) / len(self.members)

    @property
    def needs_healing(self) -> bool:
        if not self.members:
            return False
        return any(p.hp_percentage < 0.20 or p.status != "OK" for p in self.members)


@dataclass
class BattleState:
    """Estado do combate atual."""
    in_battle: bool = False
    turn_count: int = 0
    opponent_name: Optional[str] = None
    opponent_level: int = 1
    opponent_hp_percentage: float = 1.0
    opponent_status: str = "OK"
    is_shiny: bool = False


@dataclass
class QuestState:
    """Estado da missão/quest ativa."""
    active: bool = False
    quest_name: Optional[str] = None
    objective: Optional[str] = None
    target_npc: Optional[str] = None
    goto_button_visible: bool = False
    talk_button_visible: bool = False


@dataclass
class AgentState:
    """Estado interno e metas do próprio Agente."""
    current_goal: str = "IDLE"
    current_subgoal: str = "IDLE"
    active_skill: Optional[str] = None
    is_paused: bool = False
    is_running: bool = True
    last_action_time: float = field(default_factory=time.time)


@dataclass
class WorldState:
    """
    WorldState - Modelo Global do Mundo.
    Todas as observações atualizam este objeto central.
    """
    player: PlayerState = field(default_factory=PlayerState)
    team: TeamState = field(default_factory=TeamState)
    battle: BattleState = field(default_factory=BattleState)
    quest: QuestState = field(default_factory=QuestState)
    agent: AgentState = field(default_factory=AgentState)
    last_update: float = field(default_factory=time.time)
    raw_data: Dict[str, Any] = field(default_factory=dict)

    def update_timestamp(self) -> None:
        self.last_update = time.time()
