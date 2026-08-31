"""
Capabilities Registry - Registro Dinâmico de Capacidades
========================================================

Rastreia dinamicamente quais capacidades e serviços do agente estão operacionais no momento.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

from typing import Dict, Set


class CapabilitiesRegistry:
    """Registro dinâmico de capacidades ativas."""

    def __init__(self):
        self.active_capabilities: Set[str] = {
            "PERCEPTION_AVAILABLE",
            "NAVIGATION_AVAILABLE",
            "BATTLE_AVAILABLE",
            "AUTONOMY_AVAILABLE",
            "MEMORY_AVAILABLE",
            "INTERACTION_AVAILABLE",
        }

    def enable(self, capability: str) -> None:
        self.active_capabilities.add(capability.upper())

    def disable(self, capability: str) -> None:
        self.active_capabilities.discard(capability.upper())

    def is_available(self, capability: str) -> bool:
        return capability.upper() in self.active_capabilities
