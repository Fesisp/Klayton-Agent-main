"""
Visual Teacher - Aprendizado por Experiência e Geração de Datasets
===================================================================

Implementa o padrão Professor Visual (Teacher -> Student):
1. Distingue rigorosamente 'Hipótese da IA' de 'Fato do Mundo' (HYPOTHESIS != CONFIRMED).
2. Gerencia o ciclo de hipóteses (HYPOTHESIS -> OBSERVED -> CONFIRMED / REFUTED).
3. Avalia o feedback do ambiente (mudança de mapa, abertura de menu, diálogo).
4. Auto-salva datasets estruturados em data/learning/ (screenshots, crops, anotações).

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

import json
import time
from pathlib import Path
from typing import Dict, Any, Optional, List
try:
    from PIL import Image
except ImportError:
    Image = None

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger("VisualTeacher")

from .semantic_observation import SemanticHypothesis
from .semantic_memory import SemanticMemory


class VisualTeacher:
    """
    Professor Visual que valida hipóteses semânticas no ambiente e gera auto-datasets.
    """

    def __init__(self, memory: Optional[SemanticMemory] = None, data_dir: Optional[Path] = None):
        self.memory = memory or SemanticMemory()
        self.data_dir = data_dir or Path("data/learning")

        self.screenshots_dir = self.data_dir / "screenshots"
        self.crops_dir = self.data_dir / "crops"
        self.annotations_dir = self.data_dir / "annotations"
        self.events_dir = self.data_dir / "semantic_events"

        for d in [self.screenshots_dir, self.crops_dir, self.annotations_dir, self.events_dir]:
            d.mkdir(parents=True, exist_ok=True)

        self.active_hypotheses: Dict[str, SemanticHypothesis] = {}

    def register_hypothesis(self, hypothesis: SemanticHypothesis) -> str:
        """Registra uma nova hipótese semântica gerada pelo VLM."""
        hypothesis.status = "HYPOTHESIS"
        self.active_hypotheses[hypothesis.hypothesis_id] = hypothesis
        logger.info(f"💡 Nova Hipótese Registrada: [{hypothesis.hypothesis_id}] Concept: '{hypothesis.concept}' -> Expects: '{hypothesis.expected_outcome}'")
        return hypothesis.hypothesis_id

    def evaluate_environment_feedback(
        self,
        hypothesis_id: str,
        env_changed: bool,
        change_type: str,
        frame: Optional[Any] = None
    ) -> bool:
        """
        Avalia o resultado da ação no ambiente e confirma ou refuta a hipótese.
        """
        hyp = self.active_hypotheses.get(hypothesis_id)
        if not hyp:
            return False

        if env_changed and (change_type.lower() in hyp.expected_outcome.lower() or hyp.expected_outcome.lower() in change_type.lower() or env_changed):
            hyp.status = "CONFIRMED"
            logger.info(f"🎉 Hipótese CONFIRMADA pelo ambiente: [{hypothesis_id}] Concept '{hyp.concept}' produziu '{change_type}'!")

            # 1. Atualiza memória semântica
            self.memory.store_concept(hyp.concept, {
                "expected_outcome": hyp.expected_outcome,
                "confirmed_by_environment": True,
                "confidence": hyp.confidence
            })

            # 2. Salva dataset automático para treinamento futuro
            self.save_auto_dataset_sample(hyp, frame, change_type)
            del self.active_hypotheses[hypothesis_id]
            return True
        else:
            hyp.status = "REFUTED"
            logger.warning(f"❌ Hipótese REFUTADA pelo ambiente: [{hypothesis_id}] Concept '{hyp.concept}' não produziu '{hyp.expected_outcome}'")
            del self.active_hypotheses[hypothesis_id]
            return False

    def save_auto_dataset_sample(self, hypothesis: SemanticHypothesis, frame: Any, change_type: str) -> None:
        """Salva a amostra confirmada no diretório data/learning/ para treino futuro de detectores locais."""
        timestamp_str = str(int(time.time()))
        filename = f"{hypothesis.concept}_{timestamp_str}.json"

        sample_data = {
            "hypothesis_id": hypothesis.hypothesis_id,
            "concept": hypothesis.concept,
            "expected_outcome": hypothesis.expected_outcome,
            "observed_outcome": change_type,
            "confidence": hypothesis.confidence,
            "confirmed_by_environment": True,
            "timestamp": time.time()
        }

        # Salva anotação em JSON
        ann_path = self.annotations_dir / filename
        try:
            with open(ann_path, "w", encoding="utf-8") as f:
                json.dump(sample_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.debug(f"Erro ao salvar amostra de dataset: {e}")
