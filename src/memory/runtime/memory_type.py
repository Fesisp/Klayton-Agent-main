"""
Memory Type - Tipos Formais de Memória
=====================================

Enumeração dos tipos de memória mantidos pela camada persistente do agent.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

from enum import Enum


class MemoryType(Enum):
    """Tipos formais de memória do Klayton 2.0."""
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"
    RELATIONSHIP = "relationship"
