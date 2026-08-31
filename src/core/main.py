#!/usr/bin/env python3
"""
Main Entrypoint - Klayton Companion Agent 2.0
==============================================

Inicializa e conecta todos os subsistemas cognitivos, periféricos e de escuta:
- Percepção Visual (ScreenCapture, OCREngine, GameStateDetector)
- Ações & Mecânicas (InputSimulator, BattleStrategy, PokemonDatabase, TeamManager)
- Cérebro Central & Agência (KlaytonCompanionAgent, GOAP, Utility AI)
- Comunicação & Escuta (HotkeyManager, UDPCommandReceiver, Live Voice)

Autor: Klayton Companion Agent Framework
Data: 2026-08-30
"""

import sys
import time
from pathlib import Path
import yaml

# Adiciona a raiz do projeto ao PYTHONPATH
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger("KlaytonMain")

from src.perception.screen_capture import ScreenCapture
from src.perception.ocr_engine import OCREngine
from src.perception.game_state_detector import GameStateDetector, GameState
from src.action.input_simulator import InputSimulator
from src.knowledge.pokemon_database import PokemonDatabase
from src.knowledge.team_manager import TeamManager
from src.decision.battle_strategy import BattleStrategy
from src.agent.companion_agent import KlaytonCompanionAgent
from src.core.hotkey_listener import HotkeyManager
from src.core.udp_receiver import UDPCommandReceiver


def setup_logging():
    """Configura o sistema de logs rotativos."""
    try:
        log_dir = ROOT_DIR / "logs"
        log_dir.mkdir(exist_ok=True)
        if hasattr(logger, 'add'):
            logger.add(
                log_dir / "klayton.log",
                rotation="10 MB",
                retention="10 days",
                level="DEBUG",
                encoding="utf-8"
            )
    except Exception:
        pass


def load_config():
    """Carrega e funde as configurações do arquivo principal e dos arquivos modulares."""
    config_path = ROOT_DIR / "config" / "settings.yaml"
    config = {}

    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            try:
                config = yaml.safe_load(f) or {}
            except Exception as e:
                if hasattr(logger, 'error'):
                    logger.error(f"Erro ao ler settings.yaml: {e}")

    # Fusão com arquivos modulares em config/
    config_dir = ROOT_DIR / "config"
    modular_files = ["agent.yaml", "voice.yaml", "perception.yaml", "navigation.yaml", "battle.yaml"]
    for mfile in modular_files:
        mpath = config_dir / mfile
        if mpath.exists():
            try:
                with open(mpath, "r", encoding="utf-8") as f:
                    mdata = yaml.safe_load(f)
                    if isinstance(mdata, dict):
                        config.update(mdata)
            except Exception:
                pass

    return config


def main():
    setup_logging()
    if hasattr(logger, 'info'):
        logger.info("🚀 Inicializando Klayton Companion Agent 2.0...")
        logger.info("🤝 Klayton Companion Agent 2.0 initialized | Waiting for valid game perception")
    
    config = load_config()

    # Inicializa Componentes Periféricos com assinaturas corretas
    screen = ScreenCapture(config)
    ocr = OCREngine(config)
    detector = GameStateDetector(screen, ocr, config)
    inputs = InputSimulator(config)
    db = PokemonDatabase()
    team = TeamManager(config, db)
    strategy = BattleStrategy(db, team, config=config)

    components = {
        'screen': screen,
        'ocr': ocr,
        'detector': detector,
        'input': inputs,
        'db': db,
        'team': team,
        'strategy': strategy
    }

    # Inicializa o Cérebro Central
    agent = KlaytonCompanionAgent(config=config, components=components)

    # Inicializa Ouvintes Periféricos (Hotkeys e UDP)
    if hasattr(HotkeyManager, 'create_and_start'):
        hotkey_mgr = HotkeyManager.create_and_start(agent, config)
    else:
        hotkey_mgr = HotkeyManager(agent, config)
        hotkey_mgr.start()

    udp_receiver = UDPCommandReceiver(agent, config)
    udp_receiver.start()

    # Inicia o Loop Principal do Runtime
    try:
        agent.run()
    except KeyboardInterrupt:
        if hasattr(logger, 'info'):
            logger.info("🛑 Klayton finalizado pelo usuário.")
    finally:
        if hasattr(hotkey_mgr, 'stop'):
            hotkey_mgr.stop()
        if hasattr(udp_receiver, 'stop'):
            udp_receiver.stop()


if __name__ == "__main__":
    main()