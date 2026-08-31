"""
Base Vision Language Provider - Interface Abstrata para Provedores de VLM
==========================================================================

Define o contrato universal desacoplado para qualquer provedor de Visão e Linguagem.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict


class VisionLanguageProvider(ABC):
    """Interface abstrata para provedores multimodais."""

    @abstractmethod
    async def analyze(
        self,
        image: Any,
        request: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Analisa a imagem e o request e retorna um dicionário estruturado."""
        raise NotImplementedError

    def analyze_sync(
        self,
        image: Any,
        request: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """Wrapper síncrono para chamada do método analítico."""
        import asyncio
        req = request or {}
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import nest_asyncio
                nest_asyncio.apply()
                return loop.run_until_complete(self.analyze(image, req))
            return loop.run_until_complete(self.analyze(image, req))
        except Exception:
            return asyncio.run(self.analyze(image, req))
