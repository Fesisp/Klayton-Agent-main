"""
Provenance - Origem e Fontes de Evidência
==========================================

Enumeração das fontes de evidência que atribuem proveniência ao conhecimento aprendido.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

from enum import Enum


class EvidenceSource(Enum):
    """Fontes formais de evidência para proveniência de memória."""
    DIRECT_OBSERVATION = "direct_observation"
    USER_CONFIRMED = "user_confirmed"
    DATABASE = "database"
    REPLAY_VALIDATED = "replay_validated"
    INFERRED = "inferred"
    VLM = "vlm"
    OCR = "ocr"
    HEURISTIC = "heuristic"
