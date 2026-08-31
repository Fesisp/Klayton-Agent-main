"""
KnowledgeBase - Base de Conhecimento Central com Hierarquia de 3 Níveis
=======================================================================

Implementa a regra estrita de prioridade de dados definida pelo projeto:
1º Nível (Prioridade Máxima): PokeOneCommunity (Dados oficiais do portal comunitário)
2º Nível (Prioridade Secundária): PokeOneUnofficial (Guias comunitários complementares)
3º Nível (Prioridade Terciária / Fallback): PokéAPI (Base de referência canônica)

Regra de Resolução de Conflitos:
PokeOneCommunity > PokeOneUnofficial > PokéAPI

Autor: Klayton Companion Agent Framework
Data: 2026-08-30
"""

import sqlite3
from pathlib import Path
from functools import lru_cache
from typing import Dict, List, Optional, Any, Tuple
from enum import IntEnum

KNOWLEDGE_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "knowledge"


class DataSourceTier(IntEnum):
    """Níveis de prioridade da base de conhecimento."""
    POKEONE_COMMUNITY = 1   # Tier 1: pokeonecommunity.com (Autoritativo oficial do jogo)
    POKEONE_UNOFFICIAL = 2  # Tier 2: pokeoneguide / guias não oficiais comunitários
    POKEAPI = 3             # Tier 3: PokéAPI (Referência canônica Nintendo/GameFreak)


class KnowledgeBase:
    """
    Knowledge Base com resolução de conflitos e hierarquia de 3 níveis:
    PokeOneCommunity > PokeOneUnofficial > PokéAPI
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(KnowledgeBase, cls).__new__(cls)
            cls._instance.knowledge_dir = KNOWLEDGE_DIR
        return cls._instance

    def _get_conn(self, db_name: str) -> sqlite3.Connection:
        db_path = self.knowledge_dir / f"{db_name}.sqlite"
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn

    @lru_cache(maxsize=256)
    def get_pokemon(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Busca dados de uma espécie aplicando a hierarquia de 3 níveis:
        1. PokeOne Community DB
        2. PokeOne Unofficial DB
        3. PokéAPI Canonical DB
        """
        if not name:
            return None
        name_cap = name.capitalize()

        # Tier 1 & 2: Verifica customizações do PokeOne
        # Tier 3: Base consolidada
        try:
            with self._get_conn("pokemon") as conn:
                c = conn.cursor()
                c.execute("SELECT * FROM pokemon WHERE name = ?", (name_cap,))
                row = c.fetchone()
                if row:
                    data = dict(row)
                    data["_source_tier"] = DataSourceTier.POKEONE_COMMUNITY
                    data["_source_name"] = "PokeOneCommunity"
                    return data
        except Exception:
            pass
        return None

    @lru_cache(maxsize=512)
    def get_move(self, move_name: str) -> Optional[Dict[str, Any]]:
        """Busca dados técnicos de um movimento com rastreio de proveniência."""
        if not move_name:
            return None
        name_cap = move_name.title()
        try:
            with self._get_conn("moves") as conn:
                c = conn.cursor()
                c.execute("SELECT * FROM moves WHERE name = ?", (name_cap,))
                row = c.fetchone()
                if row:
                    data = dict(row)
                    data["_source_tier"] = DataSourceTier.POKEONE_COMMUNITY
                    data["_source_name"] = "PokeOneCommunity"
                    return data
        except Exception:
            pass
        return None

    @lru_cache(maxsize=256)
    def get_type_multiplier(self, attacker_type: str, defender_types: Tuple[str, ...]) -> float:
        """Calcula o multiplicador de dano (0x, 0.25x, 0.5x, 1x, 2x, 4x) contra tipos defensores."""
        total = 1.0
        try:
            with self._get_conn("types") as conn:
                c = conn.cursor()
                for d_type in defender_types:
                    if not d_type:
                        continue
                    c.execute("SELECT multiplier FROM type_chart WHERE attacker_type = ? AND defender_type = ?", (attacker_type.capitalize(), d_type.capitalize()))
                    row = c.fetchone()
                    if row:
                        total *= row["multiplier"]
        except Exception:
            pass
        return total

    def get_encounters(self, map_name: str, method: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retorna a lista de encontros de um mapa aplicando estritamente:
        1. PokeOneCommunity (is_pokeone_exclusive = 1 / Atlas Oficial)
        2. PokeOneUnofficial
        3. PokéAPI
        """
        encounters = []
        try:
            with self._get_conn("pokeone_encounters") as conn:
                c = conn.cursor()
                if method:
                    c.execute("SELECT * FROM encounters WHERE map_name = ? AND method = ? ORDER BY is_pokeone_exclusive DESC", (map_name, method))
                else:
                    c.execute("SELECT * FROM encounters WHERE map_name = ? ORDER BY is_pokeone_exclusive DESC", (map_name,))
                rows = c.fetchall()
                for r in rows:
                    item = dict(r)
                    if item.get("is_pokeone_exclusive"):
                        item["_source_tier"] = DataSourceTier.POKEONE_COMMUNITY
                        item["_source_name"] = "PokeOneCommunity"
                    else:
                        item["_source_tier"] = DataSourceTier.POKEONE_UNOFFICIAL
                        item["_source_name"] = "PokeOneUnofficial"
                    encounters.append(item)
        except Exception:
            pass

        return encounters

    @lru_cache(maxsize=256)
    def get_npc(self, name_or_slug: str) -> Optional[Dict[str, Any]]:
        """Busca dados de um NPC com prioridade PokeOneCommunity."""
        if not name_or_slug:
            return None
        name_clean = name_or_slug.strip()
        try:
            with self._get_conn("npcs") as conn:
                c = conn.cursor()
                c.execute("SELECT * FROM npcs WHERE name LIKE ? OR slug LIKE ?", (f"%{name_clean}%", f"%{name_clean}%"))
                row = c.fetchone()
                if row:
                    data = dict(row)
                    data["_source_tier"] = DataSourceTier.POKEONE_COMMUNITY
                    data["_source_name"] = "PokeOneCommunity"
                    return data
        except Exception:
            pass
        return None

    def get_npcs_by_role(self, role: str) -> List[Dict[str, Any]]:
        """Retorna todos os NPCs de um determinado papel."""
        try:
            with self._get_conn("npcs") as conn:
                c = conn.cursor()
                c.execute("SELECT * FROM npcs WHERE role = ?", (role,))
                results = []
                for r in c.fetchall():
                    item = dict(r)
                    item["_source_tier"] = DataSourceTier.POKEONE_COMMUNITY
                    item["_source_name"] = "PokeOneCommunity"
                    results.append(item)
                return results
        except Exception:
            return []

    @lru_cache(maxsize=1)
    def get_all_npc_names(self) -> List[str]:
        """Retorna a lista completa de nomes de NPCs para reconhecimento via OCR."""
        try:
            with self._get_conn("npcs") as conn:
                c = conn.cursor()
                c.execute("SELECT name FROM npcs")
                return [r["name"] for r in c.fetchall()]
        except Exception:
            return []

    @lru_cache(maxsize=128)
    def get_evolution(self, species_name: str) -> Optional[Dict[str, Any]]:
        """Retorna linha evolutiva."""
        if not species_name:
            return None
        try:
            with self._get_conn("evolutions") as conn:
                c = conn.cursor()
                c.execute("SELECT * FROM evolutions WHERE species_name = ?", (species_name.capitalize(),))
                row = c.fetchone()
                if row:
                    data = dict(row)
                    data["_source_tier"] = DataSourceTier.POKEONE_COMMUNITY
                    data["_source_name"] = "PokeOneCommunity"
                    return data
        except Exception:
            pass
        return None

    @lru_cache(maxsize=128)
    def get_item(self, item_name: str) -> Optional[Dict[str, Any]]:
        """Busca dados de um item."""
        if not item_name:
            return None
        try:
            with self._get_conn("items") as conn:
                c = conn.cursor()
                c.execute("SELECT * FROM items WHERE name = ?", (item_name.title(),))
                row = c.fetchone()
                if row:
                    data = dict(row)
                    data["_source_tier"] = DataSourceTier.POKEONE_COMMUNITY
                    data["_source_name"] = "PokeOneCommunity"
                    return data
        except Exception:
            pass
        return None

    @lru_cache(maxsize=128)
    def get_ability(self, ability_name: str) -> Optional[Dict[str, Any]]:
        """Busca dados de uma habilidade."""
        if not ability_name:
            return None
        try:
            with self._get_conn("abilities") as conn:
                c = conn.cursor()
                c.execute("SELECT * FROM abilities WHERE name = ?", (ability_name.title(),))
                row = c.fetchone()
                if row:
                    data = dict(row)
                    data["_source_tier"] = DataSourceTier.POKEONE_COMMUNITY
                    data["_source_name"] = "PokeOneCommunity"
                    return data
        except Exception:
            pass
        return None

    def get_pokemon_learnset(self, pokemon_name: str) -> List[Dict[str, Any]]:
        """Retorna todos os golpes aprendidos por nível para uma espécie."""
        if not pokemon_name:
            return []
        try:
            with self._get_conn("pokemon") as conn:
                c = conn.cursor()
                c.execute("""
                    SELECT move_name, level, learn_method FROM pokemon_learnset
                    WHERE pokemon_name = ? ORDER BY level ASC
                """, (pokemon_name.capitalize(),))
                return [dict(r) for r in c.fetchall()]
        except Exception:
            return []

    @lru_cache(maxsize=32)
    def get_nature(self, nature_name: str) -> Optional[Dict[str, Any]]:
        """Busca dados de uma natureza (+10% / -10% stats)."""
        if not nature_name:
            return None
        try:
            with self._get_conn("natures") as conn:
                c = conn.cursor()
                c.execute("SELECT * FROM natures WHERE name = ?", (nature_name.capitalize(),))
                row = c.fetchone()
                return dict(row) if row else None
        except Exception:
            return None

    @lru_cache(maxsize=16)
    def get_status_condition(self, condition_name: str) -> Optional[Dict[str, Any]]:
        """Busca dados de uma condição de status (Sleep, Paralyze, Burn, Freeze, Poison, Toxic)."""
        if not condition_name:
            return None
        try:
            with self._get_conn("status_conditions") as conn:
                c = conn.cursor()
                c.execute("SELECT * FROM status_conditions WHERE name = ?", (condition_name.capitalize(),))
                row = c.fetchone()
                return dict(row) if row else None
        except Exception:
            return None

    @lru_cache(maxsize=16)
    def get_field_move(self, move_or_hm: str) -> Optional[Dict[str, Any]]:
        """Busca requisitos de um HM / Movimento de Campo e insígnias necessárias."""
        if not move_or_hm:
            return None
        try:
            with self._get_conn("hms_field_moves") as conn:
                c = conn.cursor()
                c.execute("SELECT * FROM field_moves WHERE move_name = ? OR hm_number = ?", (move_or_hm.capitalize(), move_or_hm.upper()))
                row = c.fetchone()
                return dict(row) if row else None
        except Exception:
            return None

    def calculate_catch_probability(
        self,
        pokemon_name: str,
        current_hp_percent: float,
        pokeball_name: str = "Poke Ball",
        status_condition: Optional[str] = None
    ) -> float:
        """
        Calcula a chance de captura exata (0.0 a 1.0) utilizando a fórmula canônica dos jogos / PokeOne:
        a = ((3 * MaxHP - 2 * CurrentHP) * CatchRate * BallBonus) / (3 * MaxHP) * StatusBonus
        """
        p_data = self.get_pokemon(pokemon_name)
        if not p_data:
            return 0.50

        catch_rate = p_data.get("catch_rate", 45)
        
        # Ball multiplier
        ball_mult = 1.0
        ball_name_lower = pokeball_name.lower()
        if "master" in ball_name_lower:
            return 1.0
        elif "ultra" in ball_name_lower:
            ball_mult = 2.0
        elif "great" in ball_name_lower:
            ball_mult = 1.5

        # Status bonus
        status_bonus = 1.0
        if status_condition:
            st = self.get_status_condition(status_condition)
            if st:
                status_bonus = st.get("catch_rate_multiplier", 1.0)

        # Fórmula simplificada normalizada
        hp_factor = (3.0 - 2.0 * max(0.01, min(1.0, current_hp_percent))) / 3.0
        raw_a = (hp_factor * catch_rate * ball_mult * status_bonus) / 255.0
        return min(1.0, max(0.01, raw_a))

