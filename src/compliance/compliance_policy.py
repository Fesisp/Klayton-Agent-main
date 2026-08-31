"""
Compliance Policy - Política de Operação Segura e Supervisão Humana
===================================================================

Define os parâmetros imutáveis de limitação de taxa, tempo de sessão, confiança e foco de janela.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CompliancePolicy:
    """Política imutável de compliance e supervisão humana."""
    max_actions_per_second: float = 8.0

    max_continuous_session_minutes: int = 60

    max_identical_actions_in_window: int = 10
    repetitive_window_seconds: float = 30.0

    pause_on_low_confidence: bool = True
    minimum_world_confidence: float = 0.70

    require_correct_window_focus: bool = True
    require_manual_resume_after_guard_trigger: bool = True
