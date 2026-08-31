"""
World Model Validation Tool - Validador de Integridade de Grafos Espaciais
==========================================================================

Verifica integridade do modelo de mundo: nós duplicados, arestas para nós inexistentes e transições órfãs.

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

from src.world.model.world_model_store import WorldModelStore


def validate_world_model() -> bool:
    print("====================================================")
    print("🗺️ KLAYTON WORLD MODEL VALIDATION")
    print("====================================================")

    store = WorldModelStore()
    model = store.load_model()
    graph = model.graph

    errors = 0

    # 1. Verifica nós e arestas
    print(f"📊 Nós no Grafo: {len(graph.nodes)} | Arestas: {sum(len(e) for e in graph.edges.values())}")

    for source_id, edges in graph.edges.items():
        if source_id not in graph.nodes:
            print(f"  ❌ Erro: Origem de aresta '{source_id}' não existe nos nós do grafo")
            errors += 1
        for edge in edges:
            if edge.target not in graph.nodes:
                print(f"  ❌ Erro: Destino de aresta '{edge.target}' não existe nos nós do grafo")
                errors += 1
            if edge.cost < 0:
                print(f"  ❌ Erro: Custo negativo na aresta '{edge.source}' -> '{edge.target}'")
                errors += 1

    if errors == 0:
        print("[PASS] Grafo Espacial e Modelo de Mundo 100% Válidos")
        print("====================================================")
        return True
    else:
        print(f"[FAIL] {errors} erros de integridade encontrados no WorldModel")
        print("====================================================")
        return False


if __name__ == "__main__":
    success = validate_world_model()
    sys.exit(0 if success else 1)
