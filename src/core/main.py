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
from loguru import logger
from src.agent.companion_agent import KlaytonCompanionAgent
from src.perception.screen import ScreenCapture
from src.perception.ocr import OCREngine
from src.perception.game_state_detector import GameStateDetector
from src.mechanics.input_simulator import InputSimulator
from src.mechanics.battle_strategy import BattleStrategy
from src.mechanics.pokemon_db import PokemonDatabase
from src.mechanics.team_manager import TeamManager
from src.core.hotkey_manager import HotkeyManager
from src.core.remote_controller import create_udp_receiver


def setup_logging():
    """Configura o sistema de logs do Loguru."""
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


def load_config():
    """Carrega as configurações do arquivo settings.yaml."""
    config_path = ROOT_DIR / "config" / "settings.yaml"
    if not config_path.exists():
        logger.error(f"Arquivo de configuração não encontrado em: {config_path}")
        sys.exit(1)
        
    with open(config_path, "r", encoding="utf-8") as f:
        try:
            return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Erro ao ler settings.yaml: {e}")
            sys.exit(1)


def main():
    """Função principal que inicializa os componentes e roda o KlaytonCompanionAgent."""
    try:
        setup_logging()
        config = load_config()
        
        # 1. Inicializa componentes de percepção e mecânicas
        screen = ScreenCapture(config)
        ocr = OCREngine(config['ocr']['tesseract_path'])
        detector = GameStateDetector(screen, ocr, config)
        input_sim = InputSimulator(config)
        db = PokemonDatabase()
        team_mgr = TeamManager()
        strategy = BattleStrategy(db, team_mgr, config)
        
        components = {
            'screen': screen,
            'detector': detector,
            'input': input_sim,
            'ocr': ocr,
            'strategy': strategy,
            'team_mgr': team_mgr
        }
        
        # 2. Inicializa o Klayton Companion Agent como Cérebro e Executor Único
        agent = KlaytonCompanionAgent(config=config, components=components)
        
        # 3. Inicializa hotkey listener conectado ao Companion Agent
        hotkey_listener = None
        if config.get('controls', {}).get('enabled', True):
            try:
                hotkey_listener = HotkeyManager.create_and_start(agent, config)
                logger.success("✅ Hotkey listener ativo! Pressione as teclas para controlar o Klayton.")
            except Exception as e:
                logger.error(f"Erro ao iniciar hotkey listener: {e}")
                logger.warning("Klayton continuará sem controles por hotkey")
        
        # 4. Inicializa receptor UDP para controle remoto (se habilitado)
        udp_receiver = None
        if config.get('remote_control', {}).get('enabled', False):
            try:
                udp_receiver = create_udp_receiver(agent, config)
                if udp_receiver:
                    udp_receiver.start()
                    logger.success("✅ Controle remoto UDP ativo!")
            except Exception as e:
                logger.error(f"Erro ao iniciar controle remoto UDP: {e}")
                logger.warning("Klayton continuará sem controle remoto")
        
        # 5. Executa o loop principal diretamente no KlaytonCompanionAgent
        agent.run()
        
    except Exception as e:
        logger.critical(f"Erro fatal durante inicialização do Klayton: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()