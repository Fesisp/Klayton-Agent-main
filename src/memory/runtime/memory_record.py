"""
Memory Record - Estrutura Imutável de Registro de Memória
==========================================================

Registro individual contendo tipo, chave, valor, confiança, proveniência e tags.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Set
from .memory_type import MemoryType
from .provenance import EvidenceSource


@dataclass
class MemoryRecord:
    """Registro estruturado de memória."""
    id: str = field(default_factory=lambda: uuid.uuid4().hex)
    type: MemoryType = MemoryType.EPISODIC

    key: str = ""
    value: Any = None

    confidence: float = 0.50
    source: EvidenceSource = EvidenceSource.DIRECT_OBSERVATION

    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

    observations: int = 1
    tags: Set[str] = field(default_factory=set)

    metadata: Dict[str, Any] = field(default_factory=dict)
    superseded_by: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type.value,
            "key": self.key,
            "value": self.value,
            "confidence": self.confidence,
            "source": self.source.value,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "observations": self.observations,
            "tags": list(self.tags),
            "metadata": self.metadata,
            "superseded_by": self.superseded_by,
        }
