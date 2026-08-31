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
class Observation:
    """
    Observação bruta emitida pela percepção visual/OCR com nível de confiança.
    """
    category: str  # battle, team, location, player, quest
    data: Dict[str, Any]
    confidence: float = 1.0  # 0.0 a 1.0
    timestamp: float = field(default_factory=time.time)


@dataclass
class PokemonInfo:
    """Informações detalhadas de um Pokémon da equipe ou inimigo."""
    name: str = "Unknown"
    level: int = 1
    hp_percentage: float = 1.0  # 0.0 a 1.0
    max_hp: int = 100
    current_hp: int = 100
    status: str = "OK"  # OK, Poison, Burn, Sleep, Freeze, Paralyze
    fainted: bool = False
    active: bool = False
    moves: List[Dict[str, Any]] = field(default_factory=list)
    catch_rate: float = 1.0


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
        return any(p.hp_percentage < 0.20 or p.status != "OK" or p.fainted for p in self.members)


@dataclass
class BattleState:
    """Estado do combate atual."""
    in_battle: bool = False
    turn_count: int = 0
    opponent_name: Optional[str] = None
    opponent_level: int = 1
    opponent_hp_percentage: float = 1.0
    opponent_status: str = "OK"
    battle_type: str = "wild"  # wild ou trainer
    is_shiny: bool = False
    available_actions: List[str] = field(default_factory=lambda: ["fight", "bag", "pokemon", "run"])


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
class LocationState:
    """Estado de localização e navegação global."""
    current_map: str = "Unknown"
    region: str = "Kanto"
    coordinates: Tuple[int, int] = (0, 0)
    nearby_exits: List[str] = field(default_factory=list)
    important_landmarks: List[str] = field(default_factory=list)


@dataclass
class ResourcesState:
    """Estado de recursos e inventário."""
    pokeballs_count: int = 10
    potions_count: int = 5
    money: int = 1000
    items: Dict[str, int] = field(default_factory=dict)


@dataclass
class CompanionState:
    """Estado do companheiro em relação ao líder."""
    target_player_position: Optional[Tuple[int, int]] = None
    is_following_leader: bool = False
    leader_last_seen_timestamp: float = field(default_factory=time.time)
    leader_distance: float = 0.0


@dataclass
class WorldState:
    """
    WorldState - Modelo Global do Mundo (Fonte Única da Verdade).
    Todas as observações e PerceptionSnapshots atualizam este objeto central.
    """
    player: PlayerState = field(default_factory=PlayerState)
    team: TeamState = field(default_factory=TeamState)
    battle: BattleState = field(default_factory=BattleState)
    quest: QuestState = field(default_factory=QuestState)
    location: LocationState = field(default_factory=LocationState)
    resources: ResourcesState = field(default_factory=ResourcesState)
    companion: CompanionState = field(default_factory=CompanionState)
    agent: AgentState = field(default_factory=AgentState)
    last_update: float = field(default_factory=time.time)
    raw_data: Dict[str, Any] = field(default_factory=dict)

    def update_timestamp(self) -> None:
        self.last_update = time.time()

    def update_player(self, position: Optional[Tuple[int, int]] = None, map_name: Optional[str] = None, money: Optional[int] = None) -> None:
        self.update_timestamp()
        if position is not None:
            self.player.position = position
        if map_name is not None:
            self.player.map_name = map_name
            self.location.current_map = map_name
        if money is not None:
            self.player.money = money
            self.resources.money = money

    def update_team(self, members: Optional[List[PokemonInfo]] = None, active_index: Optional[int] = None) -> None:
        self.update_timestamp()
        if members is not None:
            self.team.members = members
        if active_index is not None:
            self.team.active_index = active_index

    def update_battle(
        self,
        in_battle: Optional[bool] = None,
        opponent_name: Optional[str] = None,
        opponent_level: Optional[int] = None,
        opponent_hp_percentage: Optional[float] = None,
        opponent_status: Optional[str] = None,
        is_shiny: Optional[bool] = None,
        battle_type: Optional[str] = None,
        available_actions: Optional[List[str]] = None
    ) -> None:
        self.update_timestamp()
        if in_battle is not None:
            self.battle.in_battle = in_battle
        if opponent_name is not None:
            self.battle.opponent_name = opponent_name
        if opponent_level is not None:
            self.battle.opponent_level = opponent_level
        if opponent_hp_percentage is not None:
            self.battle.opponent_hp_percentage = opponent_hp_percentage
        if opponent_status is not None:
            self.battle.opponent_status = opponent_status
        if is_shiny is not None:
            self.battle.is_shiny = is_shiny
        if battle_type is not None:
            self.battle.battle_type = battle_type
        if available_actions is not None:
            self.battle.available_actions = available_actions

    def update_location(self, current_map: Optional[str] = None, region: Optional[str] = None, coordinates: Optional[Tuple[int, int]] = None) -> None:
        self.update_timestamp()
        if current_map is not None:
            self.location.current_map = current_map
            self.player.map_name = current_map
        if region is not None:
            self.location.region = region
        if coordinates is not None:
            self.location.coordinates = coordinates
            self.player.position = coordinates

    def update_resources(self, pokeballs_count: Optional[int] = None, potions_count: Optional[int] = None, money: Optional[int] = None) -> None:
        self.update_timestamp()
        if pokeballs_count is not None:
            self.resources.pokeballs_count = pokeballs_count
        if potions_count is not None:
            self.resources.potions_count = potions_count
        if money is not None:
            self.resources.money = money
            self.player.money = money

    def update_companion(self, target_player_position: Optional[Tuple[int, int]] = None, is_following_leader: Optional[bool] = None, leader_distance: Optional[float] = None) -> None:
        self.update_timestamp()
        if target_player_position is not None:
            self.companion.target_player_position = target_player_position
        if is_following_leader is not None:
            self.companion.is_following_leader = is_following_leader
        if leader_distance is not None:
            self.companion.leader_distance = leader_distance

    def update_quest(self, active: Optional[bool] = None, quest_name: Optional[str] = None, objective: Optional[str] = None, target_npc: Optional[str] = None) -> None:
        self.update_timestamp()
        if active is not None:
            self.quest.active = active
        if quest_name is not None:
            self.quest.quest_name = quest_name
        if objective is not None:
            self.quest.objective = objective
        if target_npc is not None:
            self.quest.target_npc = target_npc

    def apply_snapshot(self, snapshot: Any) -> bool:
        """Aplica um PerceptionSnapshot padronizado diretamente ao WorldState."""
        if not snapshot:
            return False
        self.update_timestamp()

        if hasattr(snapshot, 'game_state'):
            self.battle.in_battle = (snapshot.game_state == "IN_BATTLE")
        if hasattr(snapshot, 'current_map') and snapshot.current_map:
            self.update_location(current_map=snapshot.current_map)
        if hasattr(snapshot, 'player_position') and snapshot.player_position:
            self.update_player(position=snapshot.player_position)
        if hasattr(snapshot, 'team') and snapshot.team:
            self.update_team(members=snapshot.team)
        if hasattr(snapshot, 'battle') and snapshot.battle:
            b = snapshot.battle
            self.update_battle(
                in_battle=b.in_battle,
                opponent_name=b.opponent_name,
                opponent_level=b.opponent_level,
                opponent_hp_percentage=b.opponent_hp_percentage,
                opponent_status=b.opponent_status,
                is_shiny=b.is_shiny
            )
        if hasattr(snapshot, 'resources') and snapshot.resources:
            r = snapshot.resources
            self.update_resources(
                pokeballs_count=r.pokeballs_count,
                potions_count=r.potions_count,
                money=r.money
            )
        if hasattr(snapshot, 'quest') and snapshot.quest:
            q = snapshot.quest
            self.update_quest(
                active=q.active,
                quest_name=q.quest_name,
                objective=q.objective,
                target_npc=q.target_npc
            )
        return True

    def apply_observation(self, obs: Observation, min_confidence: float = 0.50) -> bool:
        """
        Aplica uma observação bruta ao WorldState apenas se a confiança atingir o limiar mínimo.
        Garante que o WorldState permaneça a Fonte Única da Verdade sem ruídos visuais.
        """
        if obs.confidence < min_confidence:
            return False

        self.update_timestamp()
        if obs.category == "battle":
            self.update_battle(
                in_battle=obs.data.get("in_battle"),
                is_shiny=obs.data.get("is_shiny"),
                opponent_name=obs.data.get("opponent_name"),
                opponent_hp_percentage=obs.data.get("opponent_hp_percentage"),
                opponent_level=obs.data.get("opponent_level"),
                opponent_status=obs.data.get("opponent_status")
            )

        elif obs.category == "location":
            self.update_location(
                current_map=obs.data.get("current_map") or obs.data.get("map_name"),
                coordinates=obs.data.get("position")
            )

        elif obs.category == "team":
            if "members" in obs.data:
                self.update_team(members=obs.data["members"])
            elif "hp_percentage" in obs.data and self.team.active_pokemon:
                self.team.active_pokemon.hp_percentage = float(obs.data["hp_percentage"])

        elif obs.category in ["world_sync", "resources", "player", "quest"]:
            if "in_battle" in obs.data or "is_shiny" in obs.data or "opponent_name" in obs.data:
                self.update_battle(
                    in_battle=obs.data.get("in_battle"),
                    is_shiny=obs.data.get("is_shiny"),
                    opponent_name=obs.data.get("opponent_name"),
                    opponent_hp_percentage=obs.data.get("opponent_hp_percentage")
                )
            if "current_map" in obs.data or "position" in obs.data:
                self.update_location(
                    current_map=obs.data.get("current_map"),
                    coordinates=obs.data.get("position")
                )
            if "pokeballs_count" in obs.data or "potions_count" in obs.data:
                self.update_resources(
                    pokeballs_count=obs.data.get("pokeballs_count"),
                    potions_count=obs.data.get("potions_count")
                )

        return True
