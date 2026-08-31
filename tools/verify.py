"""
Klayton Quality Gate & Verification Tool
=======================================

Executa a verificação completa de qualidade do Klayton Agent 2.0:
1. Compilação sintática do Python
2. Importações de runtime e portabilidade
3. Integridade das tabelas da Knowledge Base SQLite
4. Suíte completa de testes unitários e de integração E2E

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

import sys
import subprocess
import py_compile
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.core.runtime_health import RuntimeHealthChecker


def run_quality_gate() -> bool:
    print("====================================================")
    print("🤖 KLAYTON QUALITY GATE (VERIFY)")
    print("====================================================")

    all_passed = True

    # 1. Compilação Python
    print("\n🔍 1. Verificando Compilação Sintática do Python...")
    errors_compile = 0
    for py_file in ROOT_DIR.glob("**/*.py"):
        if "venv" in str(py_file) or ".git" in str(py_file):
            continue
        try:
            py_compile.compile(str(py_file), doraise=True)
        except Exception as e:
            print(f"  ❌ Erro de compilação em {py_file.name}: {e}")
            errors_compile += 1

    if errors_compile == 0:
        print("  [PASS] Compilação Python (100% limpa)")
    else:
        print(f"  [FAIL] {errors_compile} arquivos com erro de compilação")
        all_passed = False

    # 2. Runtime Health & Knowledge Base
    print("\n🔍 2. Verificando Saúde do Runtime e Bancos SQLite...")
    checker = RuntimeHealthChecker()
    report = checker.run()

    if report.warnings:
        for w in report.warnings:
            print(f"  ⚠️ {w}")

    if report.errors:
        for err in report.errors:
            print(f"  ❌ {err}")
        print("  [FAIL] Validação de Saúde e Bancos SQLite falhou")
        all_passed = False
    else:
        print("  [PASS] Runtime Imports e Bancos de Conhecimento Mandatórios")

    # 3. Suíte de Testes Automatizados
    print("\n🔍 3. Executando Suíte Completa de Testes Automatizados...")
    test_files = [
        "test_integrity.py",
        "tests/test_execution_coordinator.py",
        "tests/test_knowledge_health.py",
        "tests/test_platform_imports.py",
        "tests/test_autonomous_learning_system.py",
        "tests/test_self_supervised_learning.py",
        "tests/test_semantic_vision.py",
        "tests/test_perception_manager.py",
        "tests/test_e2e_real_goap_pipeline.py",
        "tests/test_e2e_goal_instance_pipeline.py",
        "tests/test_world_state_sync.py",
        "tests/test_goap_and_utility_ai.py",
        "tests/test_companion_agent_100_percent.py",
        "tests/test_pokeapi_knowledge_base.py"
    ]

    failed_tests = 0
    for tf in test_files:
        tpath = ROOT_DIR / tf
        if not tpath.exists():
            continue

        res = subprocess.run([sys.executable, str(tpath)], capture_output=True, text=True, encoding="utf-8", errors="replace")
        if res.returncode == 0:
            print(f"  ✅ {tf} passed")
        else:
            print(f"  ❌ {tf} FAILED")
            print(f"     {res.stderr.strip() or res.stdout.strip()[:200]}")
            failed_tests += 1

    if failed_tests == 0:
        print("  [PASS] Contrato do Ciclo de Vida de Skills e Suíte de Testes")
    else:
        print(f"  [FAIL] {failed_tests} testes falharam na suíte")
        all_passed = False

    print("\n====================================================")
    if all_passed:
        print("STATUS: READY")
        print("====================================================")
        return True
    else:
        print("STATUS: BLOCKED")
        print("====================================================")
        return False


if __name__ == "__main__":
    success = run_quality_gate()
    sys.exit(0 if success else 1)
