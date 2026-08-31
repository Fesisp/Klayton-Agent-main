"""
Agent Memory System - Re-exportação Consolidada
================================================

Consolida a arquitetura de memória, unificando src/memory/agent_memory.py
com src/cognition/memory_system.py para eliminar duplicidade de classes.

Autor: Klayton Agent 2.0 Framework
Data: 2026-08-30
"""

from ..cognition.memory_system import MemorySystem, MemoryEvent

# Alias para retrocompatibilidade sem duplicação de estado
AgentMemory = MemorySystem

__all__ = ["MemorySystem", "MemoryEvent", "AgentMemory"]
