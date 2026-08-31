"""
Learning System Models - Dataclasses e Enumeradores de Aprendizado
===================================================================

Define o modelo de conhecimento imutável e estruturado para o Autonomous Learning System do Klayton.

Classes principais:
- KnowledgeStatus (UNKNOWN, HYPOTHESIS, LIKELY, CONFIRMED, TRUSTED, REFUTED)
- ExplorationRisk (SAFE, MODERATE, DANGEROUS)
- LearnedFact
- LearningTest
- ValidationResult
- DecisionRecord

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional, Dict, List


class KnowledgeStatus(str, Enum):
    UNKNOWN = "unknown"
    HYPOTHESIS = "hypothesis"
    LIKELY = "likely"
    CONFIRMED = "confirmed"
    TRUSTED = "trusted"
    REFUTED = "refuted"


class ExplorationRisk(str, Enum):
    SAFE = "safe"
    MODERATE = "moderate"
    DANGEROUS = "dangerous"


@dataclass
class LearnedFact:
    concept: str
    properties: Dict[str, Any]

    confidence: float = 0.50
    observations: int = 0
    successes: int = 0
    failures: int = 0

    status: KnowledgeStatus = KnowledgeStatus.HYPOTHESIS
    source: str = "semantic_ai"

    first_seen: float = field(default_factory=time.time)
    last_seen: float = field(default_factory=time.time)

    visual_reference: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "concept": self.concept,
            "properties": self.properties,
            "confidence": self.confidence,
            "observations": self.observations,
            "successes": self.successes,
            "failures": self.failures,
            "status": str(self.status.value if isinstance(self.status, KnowledgeStatus) else self.status),
            "source": self.source,
            "first_seen": self.first_seen,
            "last_seen": self.last_seen,
            "visual_reference": self.visual_reference
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> LearnedFact:
        st_val = data.get("status", "hypothesis")
        try:
            st_enum = KnowledgeStatus(st_val)
        except ValueError:
            st_enum = KnowledgeStatus.HYPOTHESIS

        return cls(
            concept=data.get("concept", "unknown"),
            properties=data.get("properties", {}),
            confidence=float(data.get("confidence", 0.50)),
            observations=int(data.get("observations", 0)),
            successes=int(data.get("successes", 0)),
            failures=int(data.get("failures", 0)),
            status=st_enum,
            source=data.get("source", "semantic_ai"),
            first_seen=float(data.get("first_seen", time.time())),
            last_seen=float(data.get("last_seen", time.time())),
            visual_reference=data.get("visual_reference")
        )


@dataclass
class LearningTest:
    action: str
    expected_effect: str
    risk: ExplorationRisk = ExplorationRisk.SAFE
    parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ValidationResult:
    success: bool
    confidence: float
    reason: str


@dataclass
class DecisionRecord:
    goal: str
    action: str

    predicted_reward: float
    predicted_risk: float

    success: Optional[bool] = None
    actual_reward: Optional[float] = None
    duration: Optional[float] = None
    retries: int = 0
    timestamp: float = field(default_factory=time.time)
