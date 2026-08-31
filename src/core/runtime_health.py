"""
Runtime Health Checker - Verificador de Saúde e Integridade do Runtime
========================================================================

Verifica compilação de código, integridade dos bancos SQLite e componentes do sistema
antes da inicialização do Klayton 2.0.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.knowledge.knowledge_health import KnowledgeHealthChecker


@dataclass
class HealthReport:
    """Relatório estruturado de integridade do runtime."""
    ok: bool = True
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


class RuntimeHealthChecker:
    """Verificador de saúde e prontidão do runtime."""

    def run(self) -> HealthReport:
        report = HealthReport()

        # 1. Validação de Integridade da Knowledge Base
        health_checker = KnowledgeHealthChecker()
        kb_issues = health_checker.validate()

        for issue in kb_issues:
            if "CRITICAL" in issue or "ERROR" in issue:
                report.errors.append(issue)
                report.ok = False
            else:
                report.warnings.append(issue)

        # 2. Validação dos Componentes Core
        try:
            from src.agent.companion_agent import KlaytonCompanionAgent
            from src.decision.goap_planner import GOAPPlanner
            from src.agent.execution_coordinator import ExecutionCoordinator
        except Exception as e:
            report.errors.append(f"CRITICAL: Falha ao importar componentes do runtime: {e}")
            report.ok = False

        # 3. Validação dos Alertas de Plataforma
        try:
            from src.platform.audio_alerts import AudioAlertService
            alerts = AudioAlertService()
        except Exception as e:
            report.warnings.append(f"WARNING: AudioAlertService reportou aviso: {e}")

        return report
