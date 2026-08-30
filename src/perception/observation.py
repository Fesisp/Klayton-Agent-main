"""
Observation System - Percepção com Confiança
============================================

Estrutura tipada de observação contendo um índice de confiança (0.0 a 1.0).
Garante que o agente descarte observações ruidosas (< 0.50) e solicite re-observação.

Autor: Klayton Companion Agent
Data: 2026-08-30
"""

from dataclasses import dataclass
from typing import Any, Optional, Tuple


@dataclass
class Observation:
    """Uma observação individual produzida pelos sensores visuais ou OCR."""
    entity_type: str
    value: Any
    confidence: float  # 0.0 a 1.0
    bounding_box: Optional[Tuple[int, int, int, int]] = None

    @property
    def is_reliable(self) -> bool:
        """Retorna True se a observação tiver confiança suficiente (>= 50%)."""
        return self.confidence >= 0.50
