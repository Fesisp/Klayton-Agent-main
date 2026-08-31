"""
World Location - Representação Estruturada e Imutável de Localização
======================================================================

Define a localização no modelo de mundo com mapa, região, coordenadas e confiança explícita.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class LocationConfidence(Enum):
    """Nível de confiança da localização estimada."""
    UNKNOWN = "unknown"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(frozen=True)
class WorldLocation:
    """Localização imutável no modelo de mundo."""
    map_id: Optional[str] = None
    region_id: Optional[str] = None

    x: Optional[float] = None
    y: Optional[float] = None

    landmark: Optional[str] = None

    confidence: LocationConfidence = LocationConfidence.UNKNOWN
