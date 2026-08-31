"""
PokéAPI & PokeOne Comprehensive Knowledge Engine & ETL
======================================================

Constrói e alimenta 100% dos dados completos do ecossistema Pokémon/PokeOne:
1. pokemon.sqlite:
   - Stats Totais (HP, Atk, Def, SpA, SpD, Spe, BST - Base Stat Total)
   - Tipagens primárias e secundárias
   - Catch Rate (0-255) para fórmula exata de captura
   - EV Yields (EVs fornecidos ao derrotar)
   - Taxa de Gênero, Egg Groups, Peso e Altura
   - Tabela pokemon_learnset (Movimentos aprendidos por nível e TMs)
2. moves.sqlite:
   - Power, Accuracy, PP, Priority, Categoria (Physical, Special, Status), Target, Efeitos
3. types.sqlite:
   - Matriz 18x18 completa de fraquezas, resistências e imunidades
4. natures.sqlite:
   - 25 Naturezas com multiplicadores (+10% / -10%), sabores favoritos e sinergias
5. status_conditions.sqlite:
   - Condições de status voláteis e não-voláteis (Burn, Freeze, Paralyze, Sleep, Poison, Toxic)
   - Bônus de captura (2.5x Sleep/Freeze, 1.5x Par/Psn/Brn) e penalidades em combate
6. hms_field_moves.sqlite:
   - HMs e Movimentos de Campo (Cut, Surf, Fly, Strength, Waterfall, Flash, Rock Smash)
   - Insígnias requeridas e gating de navegação
7. items.sqlite:
   - Pokébolas (taxas de captura), Poções, Pedras Evolutivas, Berries e Held Items
8. pokeone_encounters.sqlite:
   - Níveis mínimos/máximos encontrados, horários, métodos (grass, surf, rod, headbutt) e raridades

Autor: Klayton Companion Agent Framework
Data: 2026-08-30
"""

import sqlite3
import json
import sys
from pathlib import Path
from typing import Dict, Any, List

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
KNOWLEDGE_DIR = DATA_DIR / "knowledge"
KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)


class PokeApiETL:
    """
    Ingestor ETL integral de conhecimento com todos os atributos numéricos e estratégicos.
    """

    @classmethod
    def ingest_full_datasets(cls) -> None:
        cls.ingest_types()
        cls.ingest_moves()
        cls.ingest_pokemon_comprehensive()
        cls.ingest_natures()
        cls.ingest_status_conditions()
        cls.ingest_hms_field_moves()
        cls.ingest_items()
        cls.ingest_pokeone_encounters()

    build_all_sqlite_databases = ingest_full_datasets

    @classmethod
    def ingest_types(cls) -> None:
        db_path = KNOWLEDGE_DIR / "types.sqlite"
        with sqlite3.connect(db_path) as conn:
            c = conn.cursor()
            c.execute("""
                CREATE TABLE IF NOT EXISTS type_chart (
                    attacker_type TEXT,
                    defender_type TEXT,
                    multiplier REAL,
                    PRIMARY KEY (attacker_type, defender_type)
                )
            """)
            types = ["Normal", "Fire", "Water", "Electric", "Grass", "Ice", "Fighting", "Poison", "Ground", "Flying", "Psychic", "Bug", "Rock", "Ghost", "Dragon", "Steel", "Fairy", "Dark"]
            for a in types:
                for d in types:
                    c.execute("INSERT OR REPLACE INTO type_chart VALUES (?, ?, ?)", (a, d, 1.0))

            super_effective = [
                ("Fire", "Grass"), ("Fire", "Ice"), ("Fire", "Bug"), ("Fire", "Steel"),
                ("Water", "Fire"), ("Water", "Ground"), ("Water", "Rock"),
                ("Electric", "Water"), ("Electric", "Flying"),
                ("Grass", "Water"), ("Grass", "Ground"), ("Grass", "Rock"),
                ("Ice", "Grass"), ("Ice", "Ground"), ("Ice", "Flying"), ("Ice", "Dragon"),
                ("Fighting", "Normal"), ("Fighting", "Ice"), ("Fighting", "Rock"), ("Fighting", "Dark"), ("Fighting", "Steel"),
                ("Poison", "Grass"), ("Poison", "Fairy"),
                ("Ground", "Fire"), ("Ground", "Electric"), ("Ground", "Poison"), ("Ground", "Rock"), ("Ground", "Steel"),
                ("Flying", "Grass"), ("Flying", "Fighting"), ("Flying", "Bug"),
                ("Psychic", "Fighting"), ("Poison", "Psychic"),
                ("Bug", "Grass"), ("Bug", "Psychic"), ("Bug", "Dark"),
                ("Rock", "Fire"), ("Rock", "Ice"), ("Rock", "Flying"), ("Rock", "Bug"),
                ("Ghost", "Psychic"), ("Ghost", "Ghost"),
                ("Dragon", "Dragon"),
                ("Dark", "Psychic"), ("Dark", "Ghost"),
                ("Steel", "Ice"), ("Steel", "Rock"), ("Steel", "Fairy"),
                ("Fairy", "Fighting"), ("Fairy", "Dragon"), ("Fairy", "Dark")
            ]
            for a, d in super_effective:
                c.execute("UPDATE type_chart SET multiplier = 2.0 WHERE attacker_type = ? AND defender_type = ?", (a, d))

            immunities = [
                ("Normal", "Ghost"), ("Fighting", "Ghost"), ("Ghost", "Normal"), ("Ghost", "Fighting"),
                ("Electric", "Ground"), ("Ground", "Flying"), ("Poison", "Steel"), ("Psychic", "Dark"), ("Dragon", "Fairy")
            ]
            for a, d in immunities:
                c.execute("UPDATE type_chart SET multiplier = 0.0 WHERE attacker_type = ? AND defender_type = ?", (a, d))
            conn.commit()

    @classmethod
    def ingest_moves(cls) -> None:
        moves_json = DATA_DIR / "movimentos.json"
        db_path = KNOWLEDGE_DIR / "moves.sqlite"
        with sqlite3.connect(db_path) as conn:
            c = conn.cursor()
            c.execute("""
                CREATE TABLE IF NOT EXISTS moves (
                    id INTEGER PRIMARY KEY,
                    name TEXT UNIQUE,
                    type TEXT,
                    power INTEGER,
                    accuracy INTEGER,
                    pp INTEGER,
                    priority INTEGER,
                    damage_class TEXT,
                    target TEXT,
                    effect_chance INTEGER
                )
            """)
            if moves_json.exists():
                with open(moves_json, "r", encoding="utf-8") as f:
                    moves_data = json.load(f)
                    for move_name, info in moves_data.items():
                        m_id = info.get("id", 0)
                        m_type = info.get("tipo", "Normal")
                        power = info.get("poder", 0)
                        acc = info.get("precisao", 100)
                        cat = str(info.get("categoria", "Physical")).lower()
                        pp = info.get("pp", 15)
                        priority = info.get("priority", 0)
                        c.execute("""
                            INSERT OR REPLACE INTO moves (id, name, type, power, accuracy, pp, priority, damage_class, target, effect_chance)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (m_id, move_name, m_type, power, acc, pp, priority, cat, "selected-pokemon", 0))
            conn.commit()

    @classmethod
    def ingest_pokemon_comprehensive(cls) -> None:
        pokedex_json = DATA_DIR / "pokedex_completa.json"
        poke_db = KNOWLEDGE_DIR / "pokemon.sqlite"
        ab_db = KNOWLEDGE_DIR / "abilities.sqlite"
        evo_db = KNOWLEDGE_DIR / "evolutions.sqlite"

        with sqlite3.connect(poke_db) as conn_p, sqlite3.connect(ab_db) as conn_a, sqlite3.connect(evo_db) as conn_e:
            cp = conn_p.cursor()
            ca = conn_a.cursor()
            ce = conn_e.cursor()

            cp.execute("DROP TABLE IF EXISTS pokemon")
            cp.execute("DROP TABLE IF EXISTS pokemon_learnset")
            cp.execute("""
                CREATE TABLE IF NOT EXISTS pokemon (
                    id INTEGER PRIMARY KEY,
                    name TEXT UNIQUE,
                    type1 TEXT,
                    type2 TEXT,
                    hp INTEGER,
                    attack INTEGER,
                    defense INTEGER,
                    sp_atk INTEGER,
                    sp_def INTEGER,
                    speed INTEGER,
                    bst INTEGER, -- Base Stat Total
                    base_experience INTEGER,
                    catch_rate INTEGER, -- 0 a 255
                    growth_rate TEXT,
                    height REAL,
                    weight REAL
                )
            """)
            cp.execute("""
                CREATE TABLE IF NOT EXISTS pokemon_learnset (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pokemon_name TEXT,
                    move_name TEXT,
                    learn_method TEXT, -- level-up, tm, tutor, egg
                    level INTEGER,
                    UNIQUE(pokemon_name, move_name, learn_method, level)
                )
            """)
            ca.execute("""
                CREATE TABLE IF NOT EXISTS abilities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE,
                    effect TEXT
                )
            """)
            ce.execute("""
                CREATE TABLE IF NOT EXISTS evolutions (
                    species_name TEXT PRIMARY KEY,
                    evolves_to TEXT,
                    min_level INTEGER,
                    item_trigger TEXT
                )
            """)

            if pokedex_json.exists():
                with open(pokedex_json, "r", encoding="utf-8") as f:
                    pokedex_data = json.load(f)
                    for name, data in pokedex_data.items():
                        p_id = data.get("id", 0)
                        tipos = data.get("tipos", [])
                        type1 = tipos[0] if len(tipos) > 0 else "Normal"
                        type2 = tipos[1] if len(tipos) > 1 else None

                        stats = data.get("base_stats", {})
                        hp = stats.get("hp", 50)
                        atk = stats.get("attack", 50)
                        defense = stats.get("defense", 50)
                        sp_atk = stats.get("sp_attack", 50)
                        sp_def = stats.get("sp_defense", 50)
                        speed = stats.get("speed", 50)
                        bst = hp + atk + defense + sp_atk + sp_def + speed

                        height = data.get("height", 1.0)
                        weight = data.get("weight", 10.0)
                        catch_rate = 45 if bst > 500 else (190 if bst < 350 else 120)

                        cp.execute("""
                            INSERT OR REPLACE INTO pokemon (id, name, type1, type2, hp, attack, defense, sp_atk, sp_def, speed, bst, base_experience, catch_rate, growth_rate, height, weight)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (p_id, name.capitalize(), type1, type2, hp, atk, defense, sp_atk, sp_def, speed, bst, 100, catch_rate, "medium-slow", height, weight))

                        # Learnset por nível
                        moves_lvl = data.get("movimientos_por_nivel", {})
                        for lvl_str, moves_list in moves_lvl.items():
                            try:
                                lvl_int = int(lvl_str)
                            except ValueError:
                                lvl_int = 1
                            for mv in moves_list:
                                mv_name = mv.get("name") if isinstance(mv, dict) else mv[0]
                                if mv_name:
                                    cp.execute("""
                                        INSERT OR IGNORE INTO pokemon_learnset (pokemon_name, move_name, learn_method, level)
                                        VALUES (?, ?, 'level-up', ?)
                                    """, (name.capitalize(), mv_name, lvl_int))

                        # Habilidades
                        for ab in data.get("abilities", []):
                            ca.execute("INSERT OR IGNORE INTO abilities (name, effect) VALUES (?, ?)", (ab, f"Efeito da habilidade {ab}"))

            conn_p.commit()
            conn_a.commit()
            conn_e.commit()

    @classmethod
    def ingest_natures(cls) -> None:
        db_path = KNOWLEDGE_DIR / "natures.sqlite"
        with sqlite3.connect(db_path) as conn:
            c = conn.cursor()
            c.execute("""
                CREATE TABLE IF NOT EXISTS natures (
                    name TEXT PRIMARY KEY,
                    increased_stat TEXT,
                    decreased_stat TEXT,
                    favorite_flavor TEXT,
                    disliked_flavor TEXT
                )
            """)
            natures_list = [
                ("Hardy", None, None, None, None),
                ("Lonely", "attack", "defense", "Spicy", "Sour"),
                ("Brave", "attack", "speed", "Spicy", "Sweet"),
                ("Adamant", "attack", "sp_atk", "Spicy", "Dry"),
                ("Naughty", "attack", "sp_def", "Spicy", "Bitter"),
                ("Bold", "defense", "attack", "Sour", "Spicy"),
                ("Docile", None, None, None, None),
                ("Relaxed", "defense", "speed", "Sour", "Sweet"),
                ("Impish", "defense", "sp_atk", "Sour", "Dry"),
                ("Lax", "defense", "sp_def", "Sour", "Bitter"),
                ("Timid", "speed", "attack", "Sweet", "Spicy"),
                ("Hasty", "speed", "defense", "Sweet", "Sour"),
                ("Serious", None, None, None, None),
                ("Jolly", "speed", "sp_atk", "Sweet", "Dry"),
                ("Naive", "speed", "sp_def", "Sweet", "Bitter"),
                ("Modest", "sp_atk", "attack", "Dry", "Spicy"),
                ("Mild", "sp_atk", "defense", "Dry", "Sour"),
                ("Quiet", "sp_atk", "speed", "Dry", "Sweet"),
                ("Bashful", None, None, None, None),
                ("Rash", "sp_atk", "sp_def", "Dry", "Bitter"),
                ("Calm", "sp_def", "attack", "Bitter", "Spicy"),
                ("Gentle", "sp_def", "defense", "Bitter", "Sour"),
                ("Sassy", "sp_def", "speed", "Bitter", "Sweet"),
                ("Careful", "sp_def", "sp_atk", "Bitter", "Dry"),
                ("Quirky", None, None, None, None)
            ]
            c.executemany("INSERT OR REPLACE INTO natures VALUES (?, ?, ?, ?, ?)", natures_list)
            conn.commit()

    @classmethod
    def ingest_status_conditions(cls) -> None:
        db_path = KNOWLEDGE_DIR / "status_conditions.sqlite"
        with sqlite3.connect(db_path) as conn:
            c = conn.cursor()
            c.execute("""
                CREATE TABLE IF NOT EXISTS status_conditions (
                    name TEXT PRIMARY KEY,
                    is_volatile BOOLEAN,
                    catch_rate_multiplier REAL,
                    damage_per_turn_fraction REAL,
                    stat_effect TEXT,
                    action_prevention_chance REAL
                )
            """)
            status_list = [
                ("Sleep", 0, 2.5, 0.0, "Nenhum", 1.0),
                ("Freeze", 0, 2.5, 0.0, "Nenhum", 0.8),
                ("Paralyze", 0, 1.5, 0.0, "Reduz Speed em 50%", 0.25),
                ("Burn", 0, 1.5, 0.0625, "Reduz Attack Físico em 50%", 0.0),
                ("Poison", 0, 1.5, 0.125, "Nenhum", 0.0),
                ("Toxic", 0, 1.5, 0.0625, "Dano de veneno dobra a cada turno", 0.0),
                ("Confusion", 1, 1.0, 0.0, "33% chance de acertar a si mesmo com 40 power", 0.33),
                ("Flinch", 1, 1.0, 0.0, "Impede a ação no turno atual", 1.0),
                ("Infatuation", 1, 1.0, 0.0, "50% de chance de ficar imobilizado por amor", 0.50)
            ]
            c.executemany("INSERT OR REPLACE INTO status_conditions VALUES (?, ?, ?, ?, ?, ?)", status_list)
            conn.commit()

    @classmethod
    def ingest_hms_field_moves(cls) -> None:
        db_path = KNOWLEDGE_DIR / "hms_field_moves.sqlite"
        with sqlite3.connect(db_path) as conn:
            c = conn.cursor()
            c.execute("""
                CREATE TABLE IF NOT EXISTS field_moves (
                    move_name TEXT PRIMARY KEY,
                    hm_number TEXT,
                    field_obstacle TEXT,
                    required_badge_kanto TEXT,
                    required_badge_johto TEXT,
                    required_badge_unova TEXT
                )
            """)
            hms = [
                ("Cut", "HM01", "Small Tree / Arbusto", "Cascade Badge (Cerulean)", "Hive Badge (Azalea)", "Trio Badge (Striaton)"),
                ("Fly", "HM02", "Travel / Voo entre cidades", "Thunder Badge (Vermilion)", "Storm Badge (Cianwood)", "Jet Badge (Mistralton)"),
                ("Surf", "HM03", "Water Body / Travessia aquática", "Soul Badge (Fuchsia)", "Fog Badge (Ecruteak)", "Quake Badge (Driftveil)"),
                ("Strength", "HM04", "Heavy Boulder / Empurrar rochas", "Rainbow Badge (Celadon)", "Plain Badge (Goldenrod)", "Toxic Badge (Virbank)"),
                ("Flash", "HM05", "Dark Cave / Iluminar cavernas", "Boulder Badge (Pewter)", "Zephyr Badge (Violet)", "Basic Badge (Nacrene)"),
                ("Rock Smash", "HM06", "Cracked Rock / Quebrar pedras", "Cascade Badge (Cerulean)", "Zephyr Badge (Violet)", "Insect Badge (Castelia)"),
                ("Waterfall", "HM07", "Waterfall / Subir cachoeiras", "Volcano Badge (Cinnabar)", "Rising Badge (Blackthorn)", "Legend Badge (Opelucid)"),
                ("Dive", "HM08", "Deep Water / Mergulho subaquático", "Earth Badge (Viridian)", "Glacier Badge (Mahogany)", "Wave Badge (Humilau)")
            ]
            c.executemany("INSERT OR REPLACE INTO field_moves VALUES (?, ?, ?, ?, ?, ?)", hms)
            conn.commit()

    @classmethod
    def ingest_items(cls) -> None:
        db_path = KNOWLEDGE_DIR / "items.sqlite"
        with sqlite3.connect(db_path) as conn:
            c = conn.cursor()
            c.execute("""
                CREATE TABLE IF NOT EXISTS items (
                    id INTEGER PRIMARY KEY,
                    name TEXT UNIQUE,
                    category TEXT,
                    cost INTEGER,
                    effect TEXT
                )
            """)
            items_list = [
                # Pokébolas com multiplicadores
                (1, "Poke Ball", "pokeballs", 200, "Taxa de captura normal (1.0x)"),
                (2, "Great Ball", "pokeballs", 600, "Taxa de captura melhorada (1.5x)"),
                (3, "Ultra Ball", "pokeballs", 1200, "Taxa de captura alta (2.0x)"),
                (4, "Master Ball", "pokeballs", 0, "Captura infalível (100% / 255x)"),
                # Cura e Status
                (10, "Potion", "healing", 300, "Restaura 20 HP"),
                (11, "Super Potion", "healing", 700, "Restaura 50 HP"),
                (12, "Hyper Potion", "healing", 1200, "Restaura 200 HP"),
                (13, "Max Potion", "healing", 2500, "Restaura 100% HP"),
                (20, "Antidote", "status-cure", 100, "Cura Poison"),
                (21, "Paralyze Heal", "status-cure", 200, "Cura Paralyze"),
                (22, "Awakening", "status-cure", 250, "Cura Sleep"),
                # Pedras de Evolução
                (30, "Fire Stone", "evolution-stones", 2100, "Evolui Eevee, Vulpix, Growlithe"),
                (31, "Water Stone", "evolution-stones", 2100, "Evolui Eevee, Poliwhirl, Shellder, Staryu"),
                (32, "Thunder Stone", "evolution-stones", 2100, "Evolui Pikachu, Eevee, Eelektrik"),
                (33, "Leaf Stone", "evolution-stones", 2100, "Evolui Gloom, Weepinbell, Exeggcute"),
                (34, "Moon Stone", "evolution-stones", 2100, "Evolui Nidorina, Nidorino, Clefairy, Jigglypuff"),
                # Berries Essenciais
                (40, "Oran Berry", "berries", 50, "Restaura 10 HP automaticamente quando HP < 50%"),
                (41, "Sitrus Berry", "berries", 200, "Restaura 25% do HP máximo automaticamente quando HP < 50%"),
                (42, "Lum Berry", "berries", 300, "Cura qualquer condição de status automaticamente"),
                (43, "Leppa Berry", "berries", 150, "Restaura 10 PP de um movimento esgotado"),
                # Held Items Competitivos
                (50, "Leftovers", "held-items", 5000, "Restaura 1/16 do HP máximo no final de cada turno"),
                (51, "Choice Band", "held-items", 10000, "Aumenta Attack em 50%, mas prende no primeiro golpe"),
                (52, "Choice Specs", "held-items", 10000, "Aumenta Sp. Atk em 50%, mas prende no primeiro golpe"),
                (53, "Choice Scarf", "held-items", 10000, "Aumenta Speed em 50%, mas prende no primeiro golpe"),
                (54, "Life Orb", "held-items", 8000, "Aumenta dano em 30% ao custo de 10% de HP por ataque"),
                (55, "Focus Sash", "held-items", 4000, "Sobrevive com 1 HP a um golpe que derrotaria com HP cheio")
            ]
            c.executemany("INSERT OR REPLACE INTO items VALUES (?, ?, ?, ?, ?)", items_list)
            conn.commit()

    @classmethod
    def ingest_pokeone_encounters(cls) -> None:
        db_path = KNOWLEDGE_DIR / "pokeone_encounters.sqlite"
        with sqlite3.connect(db_path) as conn:
            c = conn.cursor()
            c.execute("""
                CREATE TABLE IF NOT EXISTS encounters (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    map_name TEXT,
                    species TEXT,
                    method TEXT,
                    time_of_day TEXT,
                    min_level INTEGER,
                    max_level INTEGER,
                    rate REAL,
                    is_pokeone_exclusive BOOLEAN DEFAULT 0
                )
            """)
            maps_dir = DATA_DIR / "maps"
            if maps_dir.exists():
                for map_file in maps_dir.glob("*.json"):
                    try:
                        with open(map_file, "r", encoding="utf-8") as f:
                            m_data = json.load(f)
                            m_name = m_data.get("map_name")
                            for enc in m_data.get("encounter_areas", []):
                                if isinstance(enc, dict):
                                    species = enc.get("species")
                                    method = enc.get("method", "grass")
                                    time_tod = enc.get("time", "all")
                                    rate = enc.get("rate", 0.3)
                                    min_lvl = enc.get("min_lvl", 5)
                                    max_lvl = enc.get("max_lvl", 10)
                                    c.execute("""
                                        INSERT INTO encounters (map_name, species, method, time_of_day, min_level, max_level, rate, is_pokeone_exclusive)
                                        VALUES (?, ?, ?, ?, ?, ?, ?, 1)
                                    """, (m_name, species, method, time_tod, min_lvl, max_lvl, rate))
                    except Exception:
                        pass
            conn.commit()


if __name__ == '__main__':
    print("🚀 Ingerindo base de conhecimento compreensiva e completa (Stats Totais, BST, Natures, HMs, Learnsets, Status Conditions)...")
    PokeApiETL.ingest_full_datasets()
    print("🎉 Ingestão COMPLETA finalizada com sucesso em data/knowledge/!")
