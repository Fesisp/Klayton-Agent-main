"""
Skills Package - Catálogo Modular Padronizado de Habilidades do Klayton
========================================================================

Exporta as capacidades concretas divididas por domínio:
- Navegação & Movimento: FollowSkill, WaitSkill, NavigateSkill, HealSkill, RecoverSkill
- Ação & Combate: BattleSkill, HuntingSkill, CaptureSkill, FishingSkill
- Social & Utilidade: InteractionSkill, ShoppingSkill, QuestSkill, ExploreSkill

Autor: Klayton Companion Agent Framework
Data: 2026-08-30
"""

from .base_skill import BaseSkill, SkillResult, SkillStatus
from .follow_skill import FollowSkill, FollowPlayerSkill
from .wait_skill import WaitSkill
from .navigate_skill import NavigateSkill
from .heal_skill import HealSkill
from .battle_skill import BattleSkill
from .hunting_skill import HuntingSkill
from .capture_skill import CaptureSkill
from .fishing_skill import FishingSkill
from .interaction_skill import InteractionSkill
from .shopping_skill import ShoppingSkill
from .quest_skill import QuestSkill
from .explore_skill import ExploreSkill
from .recover_skill import RecoverSkill

__all__ = [
    'BaseSkill',
    'SkillResult',
    'SkillStatus',
    'FollowSkill',
    'FollowPlayerSkill',
    'WaitSkill',
    'NavigateSkill',
    'HealSkill',
    'BattleSkill',
    'HuntingSkill',
    'CaptureSkill',
    'FishingSkill',
    'InteractionSkill',
    'ShoppingSkill',
    'QuestSkill',
    'ExploreSkill',
    'RecoverSkill',
]
