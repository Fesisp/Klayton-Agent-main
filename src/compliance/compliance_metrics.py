"""
Compliance Metrics - Métricas de Supervisão e Intervenção
==========================================================

Dataclass para acumulação e reporte de estatísticas de compliance.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class ComplianceMetrics:
    """Métricas de compliance e interrupções por supervisão."""
    rate_limit_blocks: int = 0
    session_pauses: int = 0
    focus_blocks: int = 0
    low_confidence_pauses: int = 0
    repetitive_loops: int = 0
    manual_resumes: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rate_limit_blocks": self.rate_limit_blocks,
            "session_pauses": self.session_pauses,
            "focus_blocks": self.focus_blocks,
            "low_confidence_pauses": self.low_confidence_pauses,
            "repetitive_loops": self.repetitive_loops,
            "manual_resumes": self.manual_resumes,
        }
