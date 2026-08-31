"""
Test Security Isolation - Validação de Isolamento e Segurança
=============================================================

Valida o relatório do ProcessIsolationGuard e mascaramento do CredentialsManager.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.security.process_isolation_guard import ProcessIsolationGuard
from src.security.credentials_manager import CredentialsManager


def test_security_isolation_principles():
    print("🧪 Testando Segurança e Isolamento (Herança do Projeto Interview)...")

    # 1. Teste do ProcessIsolationGuard
    guard = ProcessIsolationGuard()
    report = guard.verify_isolation()
    assert report["is_out_of_process"] is True
    assert report["memory_hooking"] is False
    assert report["dll_injection"] is False
    print("  ✅ Operação Out-of-Process verificada sem hooks ou injeção de DLLs")

    # 2. Teste do CredentialsManager
    cm = CredentialsManager()
    masked = cm.mask_secret("sk-1234567890abcdefg")
    assert masked == "sk-1...defg"
    assert cm.mask_secret("short") == "***"
    print("  ✅ Mascaramento de segredos de API verificado com sucesso")


if __name__ == "__main__":
    test_security_isolation_principles()
