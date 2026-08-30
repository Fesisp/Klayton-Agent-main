"""Módulo de Skills Modulares do Klayton Agent 2.0."""
from .base_skill import BaseSkill, SkillResult
from .battle_skill import BattleSkill
from .hunting_skill import HuntingSkill

__all__ = [
    'BaseSkill',
    'SkillResult',
    'BattleSkill',
    'HuntingSkill',
]
