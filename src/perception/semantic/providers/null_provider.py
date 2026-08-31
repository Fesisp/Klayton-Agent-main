"""
Null Vision Provider - Fallback Offline Nulo
============================================

Provedor de teste e fallback para execuções offline sem VLM ativo.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

from typing import Any, Dict
from .base_provider import VisionLanguageProvider


class NullVisionProvider(VisionLanguageProvider):
    """Provedor nulo para testes e fallback seguro."""

    async def analyze(
        self,
        image: Any,
        request: Dict[str, Any],
    ) -> Dict[str, Any]:
        return {
            "scene_type": "unknown",
            "objects": []
        }
