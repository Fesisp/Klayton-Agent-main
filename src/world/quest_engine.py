"""
Quest Engine - Motor de Missões, Ginásios e Progressão de História
==================================================================

Gerencia a árvore de missões principais e secundárias do PokeOne:
- 8 Ginásios de Kanto, Johto e Unova
- Itens-chave (Bicycle, Silph Scope, Poké Flute, HMs: Cut, Fly, Surf, Strength, Flash)
- Eventos da Equipe Rocket / Plasma / Neo-Rocket
- Diálogos de NPCs que desbloqueiam novas rotas

Autor: Klayton Companion Agent Framework
Data: 2026-08-30
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum


class QuestStatus(Enum):
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


@dataclass
class QuestObjective:
    id: str
    description: str
    target_map: str
    target_npc: Optional[str] = None
    target_item: Optional[str] = None
    target_badge: Optional[str] = None
    completed: bool = False


@dataclass
class Quest:
    id: str
    title: str
    region: str
    objectives: List[QuestObjective] = field(default_factory=list)
    status: QuestStatus = QuestStatus.NOT_STARTED
    reward: Dict[str, Any] = field(default_factory=dict)

    @property
    def current_objective(self) -> Optional[QuestObjective]:
        for obj in self.objectives:
            if not obj.completed:
                return obj
        return None

    def advance(self) -> bool:
        """Avança para o próximo objetivo da quest."""
        obj = self.current_objective
        if obj:
            obj.completed = True
            if self.current_objective is None:
                self.status = QuestStatus.COMPLETED
            return True
        return False


class QuestEngine:
    """
    Motor central de quests e enredo do jogo.
    """

    def __init__(self):
        self.quests: Dict[str, Quest] = {}
        self.badges: Dict[str, List[str]] = {"Kanto": [], "Johto": [], "Unova": []}
        self.key_items: Set[str] = set()
        self._load_core_storyline()

    def _load_core_storyline(self) -> None:
        """Carrega todas as quests principais das 3 regiões."""
        # KANTO STORYLINE
        self.register_quest(Quest(
            id="kanto_gym_1",
            title="Boulder Badge - Brock",
            region="Kanto",
            objectives=[
                QuestObjective("k1_1", "Entregar Encomenda do Prof. Oak", "Viridian City", target_npc="Clerk"),
                QuestObjective("k1_2", "Atravessar Viridian Forest", "Viridian Forest"),
                QuestObjective("k1_3", "Derrotar Líder Brock no Ginásio de Pewter", "Pewter City", target_badge="Boulder Badge")
            ]
        ))
        self.register_quest(Quest(
            id="kanto_gym_2",
            title="Cascade Badge - Misty",
            region="Kanto",
            objectives=[
                QuestObjective("k2_1", "Atravessar Mt. Moon", "Mt. Moon 1F"),
                QuestObjective("k2_2", "Vencer desafio da Nugget Bridge na Rota 24", "Route 24"),
                QuestObjective("k2_3", "Ajudar Bill na Rota 25 e obter o Ticket do SS Anne", "Route 25", target_item="SS Ticket"),
                QuestObjective("k2_4", "Derrotar Líder Misty no Ginásio de Cerulean", "Cerulean City", target_badge="Cascade Badge")
            ]
        ))
        self.register_quest(Quest(
            id="kanto_gym_3",
            title="Thunder Badge - Lt. Surge",
            region="Kanto",
            objectives=[
                QuestObjective("k3_1", "Obter HM01 Cut com o Capitão do SS Anne", "Vermilion City", target_item="HM01 Cut"),
                QuestObjective("k3_2", "Resolver quebra-cabeça das lixeiras e vencer Lt. Surge", "Vermilion City", target_badge="Thunder Badge")
            ]
        ))

    def register_quest(self, quest: Quest) -> None:
        self.quests[quest.id] = quest

    def get_active_quest(self) -> Optional[Quest]:
        for q in self.quests.values():
            if q.status == QuestStatus.IN_PROGRESS:
                return q
        for q in self.quests.values():
            if q.status == QuestStatus.NOT_STARTED:
                q.status = QuestStatus.IN_PROGRESS
                return q
        return None

    def award_badge(self, region: str, badge_name: str) -> None:
        if badge_name not in self.badges.get(region, []):
            self.badges.setdefault(region, []).append(badge_name)
            active_q = self.get_active_quest()
            if active_q and active_q.current_objective and active_q.current_objective.target_badge == badge_name:
                active_q.advance()
