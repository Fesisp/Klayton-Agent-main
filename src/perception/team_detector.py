"""
Team Detector - Extrator do Estado dos 6 Pokémon da Equipe
===========================================================

Responsável por ler e extrair em tempo real do HUD/Menu/Batalha o estado dos 6 slots do time:
- Slot 1..6:
  ├ nome (str)
  ├ level (int)
  ├ hp_percentage (float 0.0 a 1.0)
  ├ max_hp (int)
  ├ current_hp (int)
  ├ status (str: "OK", "BURN", "PARALYSIS", "POISON", "SLEEP", "FREEZE", "FAINTED")
  ├ fainted (bool)
  ├ ativo (bool - Slot 1 ou ativo em batalha)
  ├ moves (List[str] - Golpes conhecidos do banco de memória)
  └ catch_rate (int)

Autor: Klayton Companion Agent Framework
Data: 2026-08-30
"""

from typing import Dict, List, Optional, Any
try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger("TeamDetector")

from ..world.world_state import PokemonInfo


class TeamDetector:
    """
    Detector visual e analítico da equipe (6 slots do time do PokeOne).
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None, components: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        components = components or {}
        self.ocr = components.get('ocr')
        self.detector = components.get('detector')
        self.team_manager = components.get('team')
        self.db = components.get('db')

    def detect_team_slots(self, frame: Optional[Any], game_state: str = "EXPLORING", battle_info: Optional[Dict[str, Any]] = None) -> List[PokemonInfo]:
        """
        Extrai a lista de 1 a 6 PokemonInfo contendo estado detalhado de cada slot.
        """
        slots: List[PokemonInfo] = []

        # 1. Tenta extrair do GameStateDetector se disponível no frame
        raw_slots = []
        if frame is not None and self.detector and hasattr(self.detector, 'get_team_slots'):
            try:
                raw_slots = self.detector.get_team_slots(frame) or []
            except Exception:
                raw_slots = []

        # 2. Se em batalha, ajusta Slot 1 com dados em tempo real da tela de combate
        if game_state in ["IN_BATTLE", "SHINY_FOUND"] and battle_info:
            player_name = battle_info.get("player_pokemon_name") or battle_info.get("active_name")
            player_level = battle_info.get("player_level", 1)
            player_hp = battle_info.get("player_hp_percentage", 1.0)
            player_status = battle_info.get("player_status", "OK")

            if player_name:
                known_moves = []
                if self.team_manager and hasattr(self.team_manager, 'get_moves_for'):
                    known_moves = self.team_manager.get_moves_for(player_name)

                slot1 = PokemonInfo(
                    name=player_name,
                    level=int(player_level) if player_level else 1,
                    hp_percentage=float(player_hp) if player_hp is not None else 1.0,
                    max_hp=int(battle_info.get("player_max_hp", 100)),
                    current_hp=int(battle_info.get("player_current_hp", int(float(player_hp or 1.0) * 100))),
                    status=str(player_status),
                    fainted=bool(player_hp <= 0 or player_status == "FAINTED"),
                    active=True,
                    moves=known_moves
                )
                slots.append(slot1)

        # 3. Adiciona os slots brutos detectados visualmente
        for idx, raw in enumerate(raw_slots):
            # Ignora duplicata do slot 1 se já foi adicionado pela batalha
            if len(slots) > 0 and idx == 0 and game_state in ["IN_BATTLE", "SHINY_FOUND"]:
                continue

            name = raw.get("name", f"Slot_{idx + 1}")
            level = int(raw.get("level", 1))
            hp_pct = float(raw.get("hp_percentage", 1.0))
            max_hp = int(raw.get("max_hp", 100))
            cur_hp = int(raw.get("current_hp", int(hp_pct * max_hp)))
            status = raw.get("status", "OK")
            is_active = bool(raw.get("active", idx == 0))
            is_fainted = bool(hp_pct <= 0 or status == "FAINTED")

            known_moves = []
            if self.team_manager and hasattr(self.team_manager, 'get_moves_for'):
                known_moves = self.team_manager.get_moves_for(name)

            slots.append(PokemonInfo(
                name=name,
                level=level,
                hp_percentage=hp_pct,
                max_hp=max_hp,
                current_hp=cur_hp,
                status=status,
                fainted=is_fainted,
                active=is_active,
                moves=known_moves
            ))

        # 4. Se nenhum slot foi lido via OCR (sem frame/sem calibração), usa a equipe salva no TeamManager se existir
        if not slots and self.team_manager and hasattr(self.team_manager, 'current_team') and self.team_manager.current_team:
            for idx, p_name in enumerate(self.team_manager.current_team):
                p_status = self.team_manager.pokemon_status.get(p_name, "OK")
                known_moves = self.team_manager.get_moves_for(p_name)
                slots.append(PokemonInfo(
                    name=p_name.capitalize(),
                    level=1,
                    hp_percentage=1.0,
                    max_hp=100,
                    current_hp=100,
                    status=p_status,
                    fainted=(p_status == "FAINTED"),
                    active=(idx == 0),
                    moves=known_moves
                ))

        return slots
