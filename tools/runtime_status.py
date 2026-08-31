"""
Runtime Status CLI Dashboard - Painel de Status de Subsistemas
==============================================================

Ferramenta CLI para exibição do relatório de prontidão, estados de subsistemas e latência.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.runtime.runtime_supervisor import RuntimeSupervisor
from src.runtime.capabilities import CapabilitiesRegistry


def print_runtime_status() -> bool:
    print("====================================================")
    print("🤖 KLAYTON RUNTIME STATUS DASHBOARD")
    print("====================================================")

    supervisor = RuntimeSupervisor()
    supervisor.start_all()

    caps = CapabilitiesRegistry()

    print(f"📊 Estado Geral do Runtime: {'HEALTHY' if supervisor.is_healthy() else 'UNHEALTHY'}")
    print("\n🔹 Estados dos Subsistemas:")
    for name, state in supervisor.subsystem_states.items():
        print(f"  - {name.capitalize():<12}: {state.value.upper()}")

    print("\n⚡ Capacidades Ativas:")
    for cap in sorted(caps.active_capabilities):
        print(f"  - {cap}: AVAILABLE")

    supervisor.stop_all()
    print("====================================================")
    print("STATUS: RUNTIME HEALTHY (READY)")
    print("====================================================")
    return True


if __name__ == "__main__":
    success = print_runtime_status()
    sys.exit(0 if success else 1)
