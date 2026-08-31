"""
Test Runtime Supervisor - Orquestração de Ciclo de Vida
========================================================

Valida a inicialização e encerramento ordenado de subsistemas e relatório de saúde.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.runtime.runtime_supervisor import RuntimeSupervisor
from src.runtime.subsystem_state import SubsystemState


def test_runtime_supervisor_lifecycle():
    print("🧪 Testando RuntimeSupervisor (Ordem de Inicialização e Parada)...")

    supervisor = RuntimeSupervisor()

    assert supervisor.start_all() is True
    assert supervisor.is_healthy() is True
    assert supervisor.subsystem_states["autonomy"] == SubsystemState.HEALTHY
    print("  ✅ Subsistemas inicializados na ordem correta e estado marcado como HEALTHY")

    assert supervisor.stop_all() is True
    assert supervisor.subsystem_states["autonomy"] == SubsystemState.STOPPED
    print("  ✅ Subsistemas encerrados na ordem inversa com sucesso")


if __name__ == "__main__":
    test_runtime_supervisor_lifecycle()
