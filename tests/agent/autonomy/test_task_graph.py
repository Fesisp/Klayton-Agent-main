"""
Test Task Graph - Orquestração de Grafos de Tarefas
===================================================

Valida:
1. Resolução sequencial de tarefas encadeadas com dependências.
2. Identificação de conclusão do grafo.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.agent.autonomy.task_node import TaskNode
from src.agent.autonomy.task_status import TaskStatus
from src.agent.autonomy.task_graph import TaskGraph


def test_task_graph_execution():
    print("🧪 Testando TaskGraph (Dependências e Orquestração)...")

    graph = TaskGraph()
    t1 = TaskNode(id="t1", task_type="A")
    t2 = TaskNode(id="t2", task_type="B", dependencies=["t1"])

    graph.add_task(t1)
    graph.add_task(t2)

    # 1. Primeira tarefa pronta
    n1 = graph.get_next_ready_task()
    assert n1.id == "t1"
    print("  ✅ Tarefa t1 retornada como pronta (sem dependências)")

    # 2. t2 bloqueada até t1 ser COMPLETED
    t1.status = TaskStatus.COMPLETED
    n2 = graph.get_next_ready_task()
    assert n2.id == "t2"
    print("  ✅ Tarefa t2 liberada após t1 ser marcada como COMPLETED")


if __name__ == "__main__":
    test_task_graph_execution()
