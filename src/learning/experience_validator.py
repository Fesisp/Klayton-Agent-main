"""
Experience Validator - Validador de Chão de Fábrica de Consequências
====================================================================

Componente responsável por extrair ground truth do ambiente comparando o estado do jogo
imediatamente ANTES e DEPOIS da execução de um teste de hipótese.

É o componente soberano do sistema: mais importante do que a própria IA generativa, pois
fornece a validação empírica irrefutável do resultado da ação no mundo do jogo.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from typing import Any, Optional
try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger("ExperienceValidator")


class ExperienceValidator:
    """
    Validador empírico de consequências de ações no ambiente do jogo.
    """

    def validate(self, before: Any, after: Any, expectation: str) -> bool:
        """
        Compara o estado do jogo antes e depois do teste e retorna True se a expectativa foi cumprida.
        """
        if before is None or after is None:
            return False

        expectation = expectation.lower()

        # 1. Validação de Mudança de Mapa (Portas, Escadas, Portais)
        if expectation == "map_changed":
            before_map = self._extract_map(before)
            after_map = self._extract_map(after)
            if before_map and after_map and before_map != after_map and after_map not in ["Unknown", ""]:
                logger.info(f"✨ Validação de mapa CONFIRMADA: '{before_map}' ➔ '{after_map}'")
                return True
            return False

        # 2. Validação de Abertura de Diálogo / Menu (NPCs, Baús, Placas)
        if expectation in ["dialog_opened", "menu_opened"]:
            before_dialog = self._extract_attr(before, "dialog_open") or (self._extract_state(before) == "DIALOG")
            after_dialog = self._extract_attr(after, "dialog_open") or (self._extract_state(after) == "DIALOG")
            if not before_dialog and after_dialog:
                logger.info("✨ Validação de diálogo CONFIRMADA: caixa de diálogo aberta no jogo!")
                return True
            return False

        # 3. Validação de Sucesso de Movimento (Grama, Caminhos)
        if expectation == "movement_success":
            before_pos = self._extract_pos(before)
            after_pos = self._extract_pos(after)
            if before_pos and after_pos and before_pos != after_pos:
                logger.info(f"✨ Validação de movimento CONFIRMADA: deslocamento de {before_pos} para {after_pos}")
                return True
            return False

        # 4. Validação de Início de Batalha (Pokémon Selvagem)
        if expectation == "battle_started":
            before_battle = self._extract_in_battle(before)
            after_battle = self._extract_in_battle(after)
            if not before_battle and after_battle:
                logger.info("⚔️ Validação de combate CONFIRMADA: batalha iniciada!")
                return True
            return False

        return False

    def _extract_map(self, snapshot: Any) -> str:
        if hasattr(snapshot, 'current_map'):
            return snapshot.current_map
        if hasattr(snapshot, 'location') and hasattr(snapshot.location, 'current_map'):
            return snapshot.location.current_map
        return ""

    def _extract_state(self, snapshot: Any) -> str:
        if hasattr(snapshot, 'game_state'):
            return snapshot.game_state
        return ""

    def _extract_pos(self, snapshot: Any) -> Optional[Any]:
        if hasattr(snapshot, 'player_position'):
            return snapshot.player_position
        if hasattr(snapshot, 'player') and hasattr(snapshot.player, 'position'):
            return snapshot.player.position
        return None

    def _extract_attr(self, snapshot: Any, attr_name: str) -> bool:
        if hasattr(snapshot, attr_name):
            return bool(getattr(snapshot, attr_name))
        return False

    def _extract_in_battle(self, snapshot: Any) -> bool:
        if hasattr(snapshot, 'battle') and snapshot.battle:
            return bool(snapshot.battle.in_battle)
        if hasattr(snapshot, 'game_state'):
            return snapshot.game_state in ["IN_BATTLE", "SHINY_FOUND"]
        return False
