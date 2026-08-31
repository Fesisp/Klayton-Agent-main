"""
Memory System - Sistema Tríplice de Memória e Aprendizado Persistente
=====================================================================

Implementa os 3 níveis de memória do Klayton:
1. Memória de Trabalho (Working Memory): Contexto imediato dos últimos 50 eventos/ações.
2. Memória Episódica (Episodic Memory): Recordações de longo prazo de eventos marcantes e conversas com Felipe.
3. Memória Semântica (Semantic Memory): Conhecimento factual do mundo, fraquezas elementares e eficácia de rotas.

Persistência garantida em disco (JSON) entre sessões de jogo.

Autor: Klayton Companion Agent Framework
Data: 2026-08-30
"""

import json
import time
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional
from pathlib import Path

MEMORY_FILE = Path(r"c:\Users\mrfel\OneDrive\Laboratorio\Developer\Klayton-Agent-main\data\memory\klayton_memory.json")
MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)


@dataclass
class MemoryEvent:
    category: str  # dialogue, battle, discovery, relationship, quest
    content: str
    timestamp: float = field(default_factory=time.time)
    importance: float = 1.0  # 0.0 a 1.0


class MemorySystem:
    """
    Sistema cognitivo de memória e retenção de experiências.
    """

    def __init__(self, persistence_file: Path = MEMORY_FILE):
        self.persistence_file = persistence_file
        self.working_memory: List[MemoryEvent] = []
        self.episodic_memory: List[MemoryEvent] = []
        self.semantic_memory: Dict[str, Any] = {
            "player_preferences": {},
            "farm_spot_efficiency": {},
            "known_shiny_encounters": [],
            "completed_milestones": []
        }
        self.load_from_disk()

    def remember(self, category: str, content: str, importance: float = 1.0) -> None:
        """Registra um evento na memória de trabalho e na episódica se for importante."""
        event = MemoryEvent(category=category, content=content, importance=importance)
        self.working_memory.append(event)
        if len(self.working_memory) > 50:
            self.working_memory.pop(0)

        if importance >= 0.60:
            self.episodic_memory.append(event)
            self.save_to_disk()

    def record_farm_efficiency(self, map_name: str, xp_per_hour: float) -> None:
        """Registra e calcula a média móvel de eficiência de treino em uma rota."""
        stats = self.semantic_memory["farm_spot_efficiency"].setdefault(map_name, {"total_runs": 0, "avg_xp_h": 0.0})
        total = stats["total_runs"]
        stats["avg_xp_h"] = (stats["avg_xp_h"] * total + xp_per_hour) / (total + 1)
        stats["total_runs"] += 1
        self.save_to_disk()

    def get_best_farming_spot(self) -> Optional[str]:
        """Retorna a rota com maior taxa de ganho de XP/h baseado em aprendizado estatístico."""
        spots = self.semantic_memory.get("farm_spot_efficiency", {})
        if not spots:
            return None
        return max(spots.items(), key=lambda item: item[1]["avg_xp_h"])[0]

    def save_to_disk(self) -> None:
        """Salva a memória em disco para continuidade entre execuções."""
        try:
            data = {
                "episodic": [asdict(e) for e in self.episodic_memory[-200:]],
                "semantic": self.semantic_memory,
                "saved_at": time.time()
            }
            with open(self.persistence_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def load_from_disk(self) -> None:
        """Carrega memórias salvas do arquivo de persistência."""
        if not self.persistence_file.exists():
            return
        try:
            with open(self.persistence_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.semantic_memory = data.get("semantic", self.semantic_memory)
                self.episodic_memory = [
                    MemoryEvent(**e) for e in data.get("episodic", [])
                ]
        except Exception:
            pass
