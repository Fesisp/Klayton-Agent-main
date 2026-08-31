"""
Test Platform Imports & Cross-Platform Portability
===================================================

Garante que os módulos principais do runtime (KlaytonCompanionAgent, GameStateDetector)
possam ser importados e testados em qualquer sistema operacional sem depender do winsound.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.platform.audio_alerts import AudioAlertService
from src.agent.companion_agent import KlaytonCompanionAgent
from src.perception.game_state_detector import GameStateDetector


def test_platform_portability_imports():
    print("🧪 Testando Importações e Portabilidade Cross-Platform...")

    alert_service = AudioAlertService()
    alert_service.warning()
    alert_service.info()
    print("  ✅ AudioAlertService instanciado e executado com segurança")

    detector = GameStateDetector()
    assert detector is not None
    print("  ✅ GameStateDetector importado e instanciado sem dependência direta de winsound")

    agent = KlaytonCompanionAgent()
    assert agent is not None
    print("  ✅ KlaytonCompanionAgent importado e instanciado sem dependência direta de winsound")


if __name__ == "__main__":
    test_platform_portability_imports()
