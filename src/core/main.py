"""
Main Entry Point - Klayton Companion Agent Runtime
=================================================

Ponto de entrada principal que inicializa os componentes periféricos e executa
o Klayton Companion Agent como Cérebro Central e Executor Nativo do Runtime.

Autor: Klayton Companion Agent Framework
Data: 2026-08-30
"""

import sys
from pathlib import Path

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

import yaml
try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger("Main")

from src.agent.companion_agent import KlaytonCompanionAgent
from src.perception.screen_capture import ScreenCapture
from src.perception.ocr_engine import OCREngine
from src.perception.game_state_detector import GameStateDetector
from src.action.input_simulator import InputSimulator
from src.decision.battle_strategy import BattleStrategy
from src.knowledge.pokemon_database import PokemonDatabase
from src.knowledge.team_manager import TeamManager
from src.core.hotkey_listener import HotkeyManager
from src.core.udp_receiver import UDPCommandReceiver


def setup_logging():
    """Configura o sistema de logs."""
    try:
        logger.remove()
        logger.add(
            sys.stderr,
            format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level="INFO"
        )
        logger.add(
            "logs/klayton_{time:YYYY-MM-DD}.log",
            rotation="500 MB",
            retention="10 days",
            level="DEBUG",
            encoding="utf-8"
        )
    except Exception:
        pass


def load_config():
    """Carrega as configurações do arquivo settings.yaml."""
    config_path = ROOT_DIR / "config" / "settings.yaml"
    if not config_path.exists():
        if hasattr(logger, 'error'):
            logger.error(f"Arquivo de configuração não encontrado em: {config_path}")
        sys.exit(1)
        
    with open(config_path, "r", encoding="utf-8") as f:
        try:
            return yaml.safe_load(f)
        except Exception as e:
            if hasattr(logger, 'error'):
                logger.error(f"Erro ao ler settings.yaml: {e}")
            sys.exit(1)


def main():
    setup_logging()
    if hasattr(logger, 'info'):
        logger.info("🚀 Inicializando Klayton Companion Agent 2.0...")
    
    config = load_config()

    # Inicializa Componentes Periféricos
    screen = ScreenCapture(config)
    ocr = OCREngine(config)
    detector = GameStateDetector(config)
    inputs = InputSimulator(config)
    db = PokemonDatabase(config)
    team = TeamManager(config, db)
    strategy = BattleStrategy(config, db)

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
        hotkey_mgr.stop()
        udp_receiver.stop()


if __name__ == "__main__":
    main()