"""
Perception Manager & Pipeline - Orquestrador da Percepção Visual e OCR
======================================================================

Centraliza e desacopla todos os detectores periféricos (ScreenCapture, GameStateDetector,
OCREngine, ChatHandler, etc.) fornecendo um contrato único e limpo:

    snapshot = perception_manager.capture_snapshot()

O Companion Agent e o WorldState não conhecem detalhes de OpenCV, MSS, PyTesseract
ou coordenadas de pixels. Se os detectores físicos não estiverem calibrados,
o PerceptionManager retorna valores seguros sem inventar dados sobre o jogo.

Autor: Klayton Companion Agent Framework
Data: 2026-08-30
"""

import time
from typing import Dict, List, Optional, Any, Tuple
try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger("PerceptionManager")

from .perception_snapshot import PerceptionSnapshot
from ..world.world_state import PokemonInfo, BattleState, ResourcesState, QuestState
from .game_state_detector import GameState, GameStateDetector
from .chat_handler import ChatHandler
from .team_detector import TeamDetector
from ..utils.placeholders import CalibrationRequired


class PerceptionManager:
    """
    Gerenciador Central de Percepção (Perception Pipeline).
    Extrai, valida e empacota observações visuais e de OCR em PerceptionSnapshots.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None, components: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        components = components or {}

        self.screen = components.get('screen')
        self.ocr = components.get('ocr')
        self.detector: Optional[GameStateDetector] = components.get('detector')
        self.team_detector: TeamDetector = TeamDetector(self.config, components)

        # Chat handler para segurança e detecção de PMs
        self.chat_handler: Optional[ChatHandler] = None
        if self.detector:
            try:
                self.chat_handler = ChatHandler(self.detector, self.config)
            except Exception:
                self.chat_handler = None

        # Camada de Inteligência Visual Semântica (Semantic Vision / Visual Reasoner)
        from .semantic.visual_reasoner import VisualReasoner
        from .semantic.perception_fusion import PerceptionFusion
        self.visual_reasoner = VisualReasoner(config=self.config)
        self.perception_fusion = PerceptionFusion()

    def capture_frame(self) -> Optional[Any]:
        """Captura um frame bruto da janela do jogo se o driver estiver ativo."""
        if self.screen and hasattr(self.screen, 'capture'):
            try:
                return self.screen.capture()
            except Exception as e:
                logger.debug(f"Falha na captura de frame: {e}")
        return None

    def check_pm_alert(self, frame: Optional[Any]) -> bool:
        """Verifica se há alertas de Mensagem Privada (PM) no chat."""
        if frame is not None and self.chat_handler:
            try:
                return self.chat_handler.check_for_alerts(frame)
            except Exception:
                return False
        return False

    def detect_game_state(self, frame: Optional[Any]) -> str:
        """Detecta o estado geral do jogo (EXPLORING, IN_BATTLE, SHINY_FOUND, UNKNOWN)."""
        if frame is None or not self.detector or not hasattr(self.detector, 'detect_state'):
            return "UNKNOWN"
        try:
            state = self.detector.detect_state(frame)
            return state.name if hasattr(state, 'name') else str(state)
        except Exception:
            return "UNKNOWN"

    def detect_battle(self, frame: Optional[Any], game_state: str) -> Optional[BattleState]:
        """Extrai informações detalhadas de combate (oponente, nível, HP, shiny)."""
        is_in_battle = (game_state == "IN_BATTLE")
        is_shiny = (game_state == "SHINY_FOUND")

        if not is_in_battle and not is_shiny:
            return BattleState(in_battle=False, is_shiny=False)

        battle_info = {}
        if frame is not None and self.detector and hasattr(self.detector, 'get_battle_info'):
            try:
                battle_info = self.detector.get_battle_info(frame) or {}
            except Exception:
                battle_info = {}

        opp_lvl = battle_info.get("opponent_level")
        opp_hp = battle_info.get("opponent_hp_percentage")

        return BattleState(
            in_battle=is_in_battle,
            is_shiny=is_shiny,
            opponent_name=battle_info.get("opponent_name"),
            opponent_level=int(opp_lvl) if opp_lvl is not None else None,
            opponent_hp_percentage=float(opp_hp) if opp_hp is not None else None,
            opponent_status=battle_info.get("opponent_status", "UNKNOWN"),
            battle_type=battle_info.get("battle_type", None)
        )

    def detect_team(self, frame: Optional[Any], game_state: str = "EXPLORING", battle_info: Optional[Dict[str, Any]] = None) -> List[PokemonInfo]:
        """
        Extrai o estado detalhado dos 6 Pokémon da equipe visíveis no HUD/menu/batalha via TeamDetector.
        """
        return self.team_detector.detect_team_slots(frame, game_state=game_state, battle_info=battle_info)

    def detect_location(self, frame: Optional[Any]) -> str:
        """Detecta o mapa atual via OCR ou template matching."""
        return "Unknown"

    def detect_player(self, frame: Optional[Any]) -> Optional[Tuple[int, int]]:
        """Detecta as coordenadas aproximadas do jogador na grade do mapa."""
        return None

    def detect_resources(self, frame: Optional[Any]) -> Optional[ResourcesState]:
        """Detecta inventário, pokébolas e poções quando a interface de bolsa/batalha está aberta."""
        return None

    def detect_quest(self, frame: Optional[Any]) -> Optional[QuestState]:
        """Detecta botões de diálogo (Talk) ou navegação de missão (Goto)."""
        return None

    def detect_nearby_players(self, frame: Optional[Any]) -> List[Dict[str, Any]]:
        """Detecta outros jogadores nas proximidades para comportamento social/stealth."""
        return []

    def capture_snapshot(self) -> PerceptionSnapshot:
        """
        Executa a captura completa de percepção do ciclo e empacota tudo em um PerceptionSnapshot.
        """
        frame = self.capture_frame()
        game_state = self.detect_game_state(frame)
        battle_state = self.detect_battle(frame, game_state)

        battle_info_dict = None
        if battle_state and battle_state.in_battle:
            battle_info_dict = {
                "opponent_name": battle_state.opponent_name,
                "opponent_hp_percentage": battle_state.opponent_hp_percentage
            }

        team_slots = self.detect_team(frame, game_state=game_state, battle_info=battle_info_dict)

        fast_confidence = 0.95 if frame is not None else 0.0

        base_snapshot = PerceptionSnapshot(
            game_state=game_state,
            current_map=self.detect_location(frame),
            player_position=self.detect_player(frame),
            team=team_slots,
            battle=battle_state,
            resources=self.detect_resources(frame),
            nearby_players=self.detect_nearby_players(frame),
            quest=self.detect_quest(frame),
            confidence=fast_confidence,
            pm_alert=self.check_pm_alert(frame)
        )

        # Otimização de Economia de API (Se a percepção rápida já possuir alta confiança >= 0.80 e estado conhecido, retorna direto)
        if fast_confidence >= 0.80 and game_state not in ["UNKNOWN", ""]:
            return base_snapshot

        # Analisa a cena semântica via VisualReasoner (VLM/Gemini se disparado pelo ConfidenceRouter ou por desconhecidos)
        event_trigger = "UNKNOWN_SCENE" if game_state == "UNKNOWN" else None
        semantic_obs = self.visual_reasoner.analyze_scene(
            frame=frame,
            fast_confidence=fast_confidence,
            event_type=event_trigger,
            context={"game_state": game_state}
        )

        # Fusão Ponderada de Percepção
        fused_snapshot = self.perception_fusion.fuse(base_snapshot, semantic_obs)
        return fused_snapshot
