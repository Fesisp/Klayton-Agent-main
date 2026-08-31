"""
Test Memory Admission - Política de Admissão e Proteção
========================================================

Valida:
1. Rejeição de OCR/VLM isolados como candidatos semânticos automáticos.
2. Exigência de confirmações repetidas (semantic_min_confirmations = 3).

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.memory.runtime.memory_record import MemoryRecord
from src.memory.runtime.provenance import EvidenceSource
from src.memory.runtime.memory_admission import MemoryAdmissionPolicy


def test_memory_admission_policy_rules():
    print("🧪 Testando MemoryAdmissionPolicy (Proteção Contra OCR/VLM Isolados)...")

    policy = MemoryAdmissionPolicy()

    # 1. OCR isolado com confiança 0.75
    rec_ocr = MemoryRecord(key="pkmn_name", value="Pikachu", confidence=0.75, source=EvidenceSource.OCR, observations=1)

    assert policy.allow_episodic(rec_ocr) is True
    assert policy.allow_semantic_candidate(rec_ocr) is False
    assert policy.allow_semantic_commit(rec_ocr) is False
    print("  ✅ Leitura OCR isolada permitida em episódios, mas rejeitada para commit semântico (Proteção Ativa)")

    # 2. Fato com 3 confirmações
    rec_confirmed = MemoryRecord(key="pkmn_name", value="Pikachu", confidence=0.90, source=EvidenceSource.DIRECT_OBSERVATION, observations=3)
    assert policy.allow_semantic_commit(rec_confirmed) is True
    print("  ✅ Fato com 3 confirmações aprovado para commit semântico com sucesso")


if __name__ == "__main__":
    test_memory_admission_policy_rules()
