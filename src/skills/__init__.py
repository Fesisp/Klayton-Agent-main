"""Módulo de Skills Modulares do Klayton Agent 2.0."""
from .base_skill import BaseSkill, SkillResult, SkillStatus
from .battle_skill import BattleSkill
from .hunting_skill import HuntingSkill
from .follow_skill import FollowPlayerSkill, FollowSkill
from .wait_skill import WaitSkill
from .heal_skill import HealSkill
from .navigate_skill import NavigateSkill
from .fishing_skill import FishingSkill
from .shop_skill import ShopSkill
from .quest_skill import QuestSkill

__all__ = [
    'BaseSkill',
    'SkillResult',
    'SkillStatus',
    'BattleSkill',
    'HuntingSkill',
    'FollowPlayerSkill',
    'FollowSkill',
    'WaitSkill',
    'HealSkill',
    'NavigateSkill',
    'FishingSkill',
    'ShopSkill',
    'QuestSkill',
]
