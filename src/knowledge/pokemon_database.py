import sqlite3
from pathlib import Path
from functools import lru_cache


class PokemonDatabase:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PokemonDatabase, cls).__new__(cls)
            cls._instance.db_path = Path(__file__).parent.parent.parent / 'data' / 'pokedex.db'
        return cls._instance

    @lru_cache(maxsize=64)
    def get_pokemon_data(self, name):
        """Busca otimizada no SQLite com persistência de tipos e habilidades."""
        if not name:
            return None
        name = name.capitalize()

        try:
            if self.db_path.exists():
                with sqlite3.connect(self.db_path) as conn:
                    conn.row_factory = sqlite3.Row
                    cursor = conn.cursor()

                    cursor.execute("SELECT * FROM pokemon WHERE name = ?", (name,))
                    row = cursor.fetchone()
                    if row:
                        pokemon = dict(row)

                        cursor.execute("SELECT type FROM types WHERE pokemon_name = ?", (name,))
                        pokemon['tipos'] = [r[0] for r in cursor.fetchall()]

                        cursor.execute("SELECT ability FROM abilities WHERE pokemon_name = ?", (name,))
                        pokemon['abilities'] = [r[0] for r in cursor.fetchall()]

                        cursor.execute("SELECT * FROM moves WHERE pokemon_name = ?", (name,))
                        moves_rows = cursor.fetchall()

                        moves_by_level = {}
                        for m in moves_rows:
                            lvl = str(m['level'])
                            if lvl not in moves_by_level:
                                moves_by_level[lvl] = []
                            moves_by_level[lvl].append([
                                m['move_name'], m['power'], m['accuracy'],
                                m['type'], m['category'], m['priority'], m['pp']
                            ])

                        pokemon['movimientos_por_nivel'] = moves_by_level
                        return pokemon
        except Exception:
            pass

        # Fallback soberano via KnowledgeBase (Tier 1 PokeOneCommunity -> Tier 3 PokeAPI)
        try:
            from .knowledge_base import KnowledgeBase
            kb = KnowledgeBase()
            kb_data = kb.get_pokemon(name)
            if kb_data:
                types_list = [t for t in [kb_data.get('type1'), kb_data.get('type2')] if t]
                return {
                    'name': kb_data.get('name', name),
                    'id': kb_data.get('id', 1),
                    'hp': kb_data.get('hp', 45),
                    'attack': kb_data.get('attack', 49),
                    'defense': kb_data.get('defense', 49),
                    'sp_attack': kb_data.get('sp_atk', 65),
                    'sp_defense': kb_data.get('sp_def', 65),
                    'speed': kb_data.get('speed', 45),
                    'height': kb_data.get('height', 0.7),
                    'weight': kb_data.get('weight', 6.9),
                    'tipos': types_list,
                    'abilities': [],
                    'movimientos_por_nivel': {}
                }
        except Exception:
            pass

        return None

    def get_all_pokemon_names(self):
        """Retorna todos os nomes oficiais para validação de OCR."""
        try:
            if self.db_path.exists():
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT name FROM pokemon")
                    names = [r[0] for r in cursor.fetchall()]
                    if names:
                        return names
        except Exception:
            pass

        try:
            from .knowledge_base import KnowledgeBase
            kb = KnowledgeBase()
            with kb._get_conn("pokemon") as conn:
                c = conn.cursor()
                c.execute("SELECT name FROM pokemon")
                return [r[0] for r in c.fetchall()]
        except Exception:
            return []

    @lru_cache(maxsize=256)
    def get_move_data(self, move_name):
        """
        Busca informações de um movimento específico no banco de dados.
        """
        if not move_name:
            return None
        
        move_key = move_name.lower().strip()
        
        try:
            if self.db_path.exists():
                with sqlite3.connect(self.db_path) as conn:
                    conn.row_factory = sqlite3.Row
                    cursor = conn.cursor()
                    
                    cursor.execute("""
                        SELECT DISTINCT move_name, power, accuracy, type, category, priority, pp
                        FROM moves
                        WHERE LOWER(move_name) = ?
                        LIMIT 1
                    """, (move_key,))
                    
                    row = cursor.fetchone()
                    if row:
                        return dict(row)
        except Exception:
            pass

        try:
            from .knowledge_base import KnowledgeBase
            kb = KnowledgeBase()
            move_data = kb.get_move(move_name)
            if move_data:
                return {
                    'move_name': move_data.get('name', move_name),
                    'power': move_data.get('power'),
                    'accuracy': move_data.get('accuracy'),
                    'type': move_data.get('type'),
                    'category': move_data.get('category'),
                    'priority': move_data.get('priority', 0),
                    'pp': move_data.get('pp', 15)
                }
        except Exception:
            pass

        return None

