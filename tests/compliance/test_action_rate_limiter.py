"""
Test Action Rate Limiter - Limitação de Taxa de Acionamentos
============================================================

Valida o bloqueio de acionamentos ao exceder a frequência máxima permitida (ex: 8 acionamentos/s).

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.compliance.action_rate_limiter import ActionRateLimiter


def test_action_rate_limiter():
    print("🧪 Testando ActionRateLimiter (Limite de 8 acionamentos/s)...")

    limiter = ActionRateLimiter(max_actions_per_second=8.0)

    for i in range(8):
        assert limiter.allow() is True

    # 9º acionamento no mesmo segundo deve ser bloqueado
    assert limiter.allow() is False
    print("  ✅ Limite de taxa de 8 acionamentos/s respeitado com sucesso")


if __name__ == "__main__":
    test_action_rate_limiter()
