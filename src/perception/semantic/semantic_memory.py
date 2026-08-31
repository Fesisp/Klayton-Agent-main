"""
Semantic Memory System - Armazenamento de Conhecimento Visual
==============================================================

Gerencia e persiste em disco (data/memory/semantic_visual/) o conhecimento visual
aprendido pelo Klayton (conceitos, cenas, regras do ambiente e instâncias de interações).

Diferente da memória episódica, guarda generalizações semânticas como:
- "pokemon_center_exit": expected_effect -> leave_building, success_rate -> 0.98

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional, List
try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger("SemanticMemory")

from .semantic_observation import SemanticObservation


class SemanticMemory:
    """
    Sistema de memória semântica persistente para conceitos e regras visuais.
    """

    def __init__(self, memory_dir: Optional[Path] = None):
        self.memory_dir = memory_dir or Path("data/memory/semantic_visual")
        self.memory_dir.mkdir(parents=True, exist_ok=True)

        self.concepts_file = self.memory_dir / "concepts.json"
        self.scene_cache_file = self.memory_dir / "scene_cache.json"
        self.rules_file = self.memory_dir / "environment_rules.json"

        self.concepts: Dict[str, Dict[str, Any]] = self._load_json(self.concepts_file)
        self.scene_cache: Dict[str, Dict[str, Any]] = self._load_json(self.scene_cache_file)
        self.environment_rules: Dict[str, Dict[str, Any]] = self._load_json(self.rules_file)

    def _load_json(self, file_path: Path) -> Dict[str, Any]:
        if file_path.exists():
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    return json.load(f) or {}
            except Exception as e:
                logger.debug(f"Erro ao carregar {file_path}: {e}")
        return {}

    def _save_json(self, file_path: Path, data: Dict[str, Any]) -> None:
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.debug(f"Erro ao salvar {file_path}: {e}")

    def store_concept(self, concept_name: str, concept_data: Dict[str, Any]) -> None:
        """Registra ou atualiza um conceito semântico aprendido."""
        existing = self.concepts.get(concept_name, {"examples_count": 0, "success_rate": 1.0})
        existing["examples_count"] = existing.get("examples_count", 0) + 1
        existing.update(concept_data)

        self.concepts[concept_name] = existing
        self._save_json(self.concepts_file, self.concepts)
        logger.info(f"🧠 Conceito semântico salvo em memória: '{concept_name}' ({existing['examples_count']} exemplos)")

    def get_concept(self, concept_name: str) -> Optional[Dict[str, Any]]:
        """Recupera um conceito semântico da memória."""
        return self.concepts.get(concept_name)

    def store_scene_cache(self, scene_hash: str, obs: SemanticObservation) -> None:
        """Guarda o resultado da análise de uma cena pelo seu hash perceptual."""
        self.scene_cache[scene_hash] = obs.to_dict()
        self._save_json(self.scene_cache_file, self.scene_cache)

    def find_matching_scene(self, scene_hash: str) -> Optional[Dict[str, Any]]:
        """Busca se a cena já foi analisada e salva previamente em cache."""
        return self.scene_cache.get(scene_hash)

    def record_environment_rule(self, rule_name: str, rule_data: Dict[str, Any]) -> None:
        """Registra uma regra de ambiente confirmada pela experiência."""
        self.environment_rules[rule_name] = rule_data
        self._save_json(self.rules_file, self.environment_rules)
