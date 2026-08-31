"""
Correction Handler - Manipulador de Correções do Usuário
========================================================

Processa correções ativas do usuário, atualizando fatos e invalidando registros anteriores via superseded_by.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

from typing import Any, Dict, Optional
from ...memory.memory_facade import MemoryFacade
from ...memory.runtime.provenance import EvidenceSource


class CorrectionHandler:
    """Manipulador de correções humanas."""

    def __init__(self, memory_facade: Optional[MemoryFacade] = None):
        self.memory = memory_facade or MemoryFacade()

    def apply_correction(self, key: str, corrected_value: Any) -> Dict[str, Any]:
        """Aplica a correção substituindo a verdade anterior com alta confiança."""
        record = self.memory.record_fact_candidate(
            key=key,
            value=corrected_value,
            source=EvidenceSource.USER_CONFIRMED,
            confidence=0.98
        )
        return {
            "status": "correction_applied",
            "key": record.key,
            "corrected_value": record.value,
            "confidence": record.confidence
        }
