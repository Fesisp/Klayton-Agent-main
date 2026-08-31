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


def run_quality_gate(is_release_mode: bool = False) -> bool:
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
        "tests/battle/runtime/test_battle_state_tracker.py",
        "tests/battle/runtime/test_battle_outcome_verifier.py",
        "tests/battle/runtime/test_battle_action_executor.py",
        "tests/battle/runtime/test_battle_session.py",
        "tests/battle/runtime/test_battle_skill_state_machine.py",
        "tools/validate_battle_runtime.py",
        "tools/validate_world_model.py",
        "tests/navigation/runtime/test_world_graph.py",
        "tests/navigation/runtime/test_localization.py",
        "tests/navigation/runtime/test_navigation_progress_verifier.py",
        "tests/navigation/runtime/test_stuck_detector.py",
        "tests/navigation/runtime/test_navigation_executor.py",
        "tests/navigation/runtime/test_route_state.py",
        "tests/navigation/runtime/test_navigation_skill_state_machine.py",
        "tools/validate_navigation_runtime.py",
        "tests/agent/autonomy/test_goal_arbitrator.py",
        "tests/agent/autonomy/test_goal_stack.py",
        "tests/agent/autonomy/test_goal_progress.py",
        "tests/agent/autonomy/test_task_graph.py",
        "tests/agent/autonomy/test_long_horizon_planner.py",
        "tests/agent/autonomy/test_loop_detector.py",
        "tests/agent/autonomy/test_autonomy_controller.py",
        "tools/validate_autonomy.py",
        "tests/memory/runtime/test_memory_record.py",
        "tests/memory/runtime/test_memory_store.py",
        "tests/memory/runtime/test_memory_admission.py",
        "tests/memory/runtime/test_memory_consolidator.py",
        "tests/memory/runtime/test_contradiction_resolver.py",
        "tests/memory/runtime/test_memory_decay.py",
        "tests/memory/runtime/test_memory_retriever.py",
        "tests/memory/runtime/test_procedural_memory.py",
        "tests/memory/runtime/test_learning_evaluator.py",
        "tools/audit_memory.py",
        "tools/replay_learning.py",
        "tests/interaction/runtime/test_context_resolver.py",
        "tests/interaction/runtime/test_command_router.py",
        "tests/interaction/runtime/test_ambiguity_resolver.py",
        "tests/interaction/runtime/test_explanation_engine.py",
        "tests/interaction/runtime/test_teaching_interpreter.py",
        "tests/interaction/runtime/test_correction_handler.py",
        "tests/interaction/runtime/test_interaction_policy.py",
        "tests/interaction/runtime/test_npc_interaction.py",
        "tools/validate_interaction.py",
        "tests/runtime/test_runtime_supervisor.py",
        "tests/runtime/test_watchdog.py",
        "tests/runtime/test_fault_manager.py",
        "tests/runtime/test_state_guard.py",
        "tests/runtime/test_resource_monitor.py",
        "tests/runtime/test_circuit_breaker.py",
        "tests/runtime/test_shutdown_manager.py",
        "tests/runtime/test_runtime_scheduler.py",
        "tests/runtime/test_input_guard.py",
        "tools/runtime_status.py",
        "tools/stress_runtime.py",
        "tools/audit_knowledge.py",
        "tools/replay_runtime_events.py",
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

    # 4. Release Audit & Environment Check (se modo --release)
    if is_release_mode:
        print("\n🔍 4. Executando Auditoria de Release e Checagem de Ambiente...")
        check_env_script = ROOT_DIR / "tools" / "check_environment.py"
        audit_script = ROOT_DIR / "tools" / "release_audit.py"

        r_env = subprocess.run([sys.executable, str(check_env_script)], capture_output=True, text=True, encoding="utf-8", errors="replace")
        r_aud = subprocess.run([sys.executable, str(audit_script)], capture_output=True, text=True, encoding="utf-8", errors="replace")

        if r_env.returncode == 0 and r_aud.returncode == 0:
            print("  [PASS] Auditoria de Release e Checagem de Ambiente (100% limpas)")
        else:
            print("  [FAIL] Falha na auditoria de release ou checagem de ambiente")
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


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Klayton Master Quality Gate")
    parser.add_argument("--quick", action="store_true", help="Executa apenas compilação e testes rápidos")
    parser.add_argument("--full", action="store_true", help="Executa suíte completa")
    parser.add_argument("--release", action="store_true", help="Executa Quality Gate completo de Release com auditorias")
    args = parser.parse_args()

    success = run_quality_gate(is_release_mode=args.release)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
