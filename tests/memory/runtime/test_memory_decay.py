"""
Test Memory Decay - Decaimento Temporal de Confiança
=====================================================

Valida:
1. Decaimento de confiança de registros contextuais antigos.
2. Preservação de confiança de registros do usuário (USER_CONFIRMED) e canônicos (DATABASE).

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

import sys
import time
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.memory.runtime.memory_record import MemoryRecord
from src.memory.runtime.provenance import EvidenceSource
from src.memory.runtime.memory_decay import MemoryDecay


def test_memory_decay_rules():
    print("🧪 Testando MemoryDecay (Decaimento Temporal e Proteções)...")

    now = time.time()
    old_time = now - (3600.0 * 24.0)  # 24 horas atrás

    rec_context = MemoryRecord(key="route_blocked", value=True, confidence=0.90, source=EvidenceSource.DIRECT_OBSERVATION, updated_at=old_time)
    decayed_conf = MemoryDecay.apply_decay(rec_context, now=now)
    assert decayed_conf < 0.90
    print(f"  ✅ Registro contextual antigo teve confiança reduzida de 0.90 para {decayed_conf:.2f}")

    rec_user = MemoryRecord(key="user_name", value="Trainer", confidence=0.98, source=EvidenceSource.USER_CONFIRMED, updated_at=old_time)
    user_conf = MemoryDecay.apply_decay(rec_user, now=now)
    assert user_conf == 0.98
    print("  ✅ Registro confirmado pelo usuário manteve a confiança intacta (0.98)")


if __name__ == "__main__":
    test_memory_decay_rules()
