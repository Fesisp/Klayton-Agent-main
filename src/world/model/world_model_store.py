"""
World Model Store - Persistência Segura do Modelo de Mundo
============================================================

Carrega dados de mapas canônicos e grava dados aprendidos isoladamente em data/runtime/world_learning/.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional
from .world_model import WorldModel


class WorldModelStore:
    """Gerenciador de armazenamento do modelo de mundo."""

    def __init__(self, data_dir: Optional[Path] = None):
        self.root_dir = data_dir or Path(__file__).resolve().parent.parent.parent.parent / "data"
        self.learning_dir = self.root_dir / "runtime" / "world_learning"
        self.learning_dir.mkdir(parents=True, exist_ok=True)

    def load_model(self) -> WorldModel:
        """Carrega e instancia o modelo de mundo inicial."""
        model = WorldModel()

        # Adiciona nós e conexões de teste/canônicos para Kanto básico
        n_pallet = model.add_location("Pallet Town", "Pallet Town", x=0.0, y=0.0, kind="landmark")
        n_route1 = model.add_location("Route 1", "Route 1", x=0.0, y=10.0, kind="route_entry")
        n_viridian = model.add_location("Viridian City", "Viridian City", x=0.0, y=20.0, kind="landmark")
        n_poke_center = model.add_location("Viridian PokéCenter", "Viridian City", x=2.0, y=22.0, kind="healing_point")

        model.add_connection("Pallet Town", "Route 1", cost=1.0, transition=True)
        model.add_connection("Route 1", "Viridian City", cost=1.0, transition=True)
        model.add_connection("Viridian City", "Viridian PokéCenter", cost=0.5, transition=False)

        return model

    def save_learned_metadata(self, metadata: dict) -> Path:
        """Salva metadados de aprendizado sem sobrescrever mapas canônicos."""
        out_file = self.learning_dir / "learned_edges.json"
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        return out_file
