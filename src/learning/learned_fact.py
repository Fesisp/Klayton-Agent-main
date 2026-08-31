"""
Learned Fact & Knowledge Status - Representação do Conhecimento Aprendido
==========================================================================

Define as estruturas imutáveis e enumeradores para o conhecimento derivado de hipóteses
visuais e validados pelo ambiente do jogo.

Princípio Fundamental:
A IA multimodal nunca ensina uma verdade absoluta. Ela propõe uma hipótese (confidence = 0.5).
O jogo confirma a verdade através da experiência e observação de consequências.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, Optional


class KnowledgeStatus(Enum):
    """Níveis de maturidade do conhecimento do agente."""
    HYPOTHESIS = "hypothesis"  # Nenhuma evidência prática (sugerido por VLM/IA)
    LIKELY = "likely"          # >= 2 sucessos observados
    CONFIRMED = "confirmed"    # >= 3 sucessos + confiança >= 0.90
    TRUSTED = "trusted"        # Dezenas de confirmações sem falhas
    REFUTED = "refuted"        # Falhas repetidas ou rejeitado por validação


class ExplorationRisk(Enum):
    """Nível de risco para exploração autônoma de hipóteses."""
    SAFE = 1        # Andar, aproximar, examinar objeto, abrir diálogo, fechar menu
    MODERATE = 2    # Usar golpe em batalha selvagem, mover item no inventário
    DANGEROUS = 3   # Comprar/vender, descartar item, trocar Pokémon permanentemente, gastar moedas


@dataclass
class LearnedFact:
    """Fato ou hipótese aprendida sobre um conceito/objeto do jogo."""
    concept: str
    properties: Dict[str, Any]
    confidence: float = 0.5
    observations: int = 0
    successes: int = 0
    failures: int = 0
    status: KnowledgeStatus = KnowledgeStatus.HYPOTHESIS
    source: str = "semantic_ai"
    risk_level: ExplorationRisk = ExplorationRisk.SAFE
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    first_seen: float = field(default_factory=time.time)
    last_seen: float = field(default_factory=time.time)
    visual_reference: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Converte a instância para um dicionário serializável."""
        return {
            "concept": self.concept,
            "properties": self.properties,
            "confidence": self.confidence,
            "observations": self.observations,
            "successes": self.successes,
            "failures": self.failures,
            "status": self.status.value if isinstance(self.status, KnowledgeStatus) else str(self.status),
            "source": self.source,
            "risk_level": self.risk_level.value if isinstance(self.risk_level, ExplorationRisk) else int(self.risk_level),
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LearnedFact":
        """Instancia um LearnedFact a partir de um dicionário."""
        status_val = data.get("status", "hypothesis")
        if isinstance(status_val, str):
            try:
                status_enum = KnowledgeStatus(status_val)
            except ValueError:
                status_enum = KnowledgeStatus.HYPOTHESIS
        else:
            status_enum = status_val

        risk_val = data.get("risk_level", 1)
        if isinstance(risk_val, int):
            try:
                risk_enum = ExplorationRisk(risk_val)
            except ValueError:
                risk_enum = ExplorationRisk.SAFE
        else:
            risk_enum = risk_val

        return cls(
            concept=data.get("concept", "unknown"),
            properties=data.get("properties", {}),
            confidence=float(data.get("confidence", 0.5)),
            observations=int(data.get("observations", 0)),
            successes=int(data.get("successes", 0)),
            failures=int(data.get("failures", 0)),
            status=status_enum,
            source=data.get("source", "semantic_ai"),
            risk_level=risk_enum,
            created_at=float(data.get("created_at", time.time())),
            updated_at=float(data.get("updated_at", time.time()))
        )
