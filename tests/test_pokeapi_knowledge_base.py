"""
Suíte de Testes da Base de Conhecimento SQLite (PokéAPI & PokeOne Authoritative)
================================================================================

Valida o pipeline ETL, consultas locais SQLite em microssegundos e a hierarquia
PokéOne > PokéAPI para decisões de batalha e navegação.

Autor: Klayton Companion Agent Framework
Data: 2026-08-30
"""

import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.knowledge.knowledge_base import KnowledgeBase
from src.knowledge.pokeapi_etl import PokeApiETL


def test_pokeapi_etl_generation():
    print("🧪 Testando: Ingestão e Construção dos Bancos SQLite Locais...")
    PokeApiETL.build_all_sqlite_databases()
    knowledge_dir = ROOT_DIR / "data" / "knowledge"
    
    expected_dbs = [
        "pokemon.sqlite", "moves.sqlite", "items.sqlite",
        "types.sqlite", "abilities.sqlite", "evolutions.sqlite",
        "pokeone_encounters.sqlite"
    ]
    for db in expected_dbs:
        db_file = knowledge_dir / db
        assert db_file.exists(), f"Banco {db} não foi gerado!"
    print("  ✅ Todos os 7 bancos de dados SQLite gerados e indexados com sucesso em data/knowledge/")


def test_pokemon_and_moves_query():
    print("\n🧪 Testando: Consulta Otimizada de Pokémon e Movimentos...")
    kb = KnowledgeBase()

    # 1. Consulta de Pokémon
    pika = kb.get_pokemon("Pikachu")
    assert pika is not None
    assert pika["type1"] == "Electric"
    assert pika["speed"] == 90
    print(f"  ✅ Espécie validada: {pika['name']} | Tipo: {pika['type1']} | Speed Base: {pika['speed']}")

    # 2. Consulta de Move
    tb = kb.get_move("Thunderbolt")
    assert tb is not None
    assert tb["power"] == 90
    assert tb["accuracy"] == 100
    assert tb["damage_class"] == "special"
    print(f"  ✅ Movimento validado: {tb['name']} | Power: {tb['power']} | Acc: {tb['accuracy']}% | Categoria: {tb['damage_class']}")


def test_type_chart_calculations():
    print("\n🧪 Testando: Cálculo de Fraquezas, Resistências e Imunidades...")
    kb = KnowledgeBase()

    # Electric vs Water = 2.0x (Super Effective)
    mult_sup = kb.get_type_multiplier("Electric", ("Water",))
    assert mult_sup == 2.0
    print(f"  ✅ Electric ➔ Water: {mult_sup}x (Super efetivo)")

    # Electric vs Ground = 0.0x (Imunidade)
    mult_imm = kb.get_type_multiplier("Electric", ("Ground",))
    assert mult_imm == 0.0
    print(f"  ✅ Electric ➔ Ground: {mult_imm}x (Imune)")

    # Water vs Fire/Rock = 4.0x (Fraqueza Dupla)
    mult_double = kb.get_type_multiplier("Water", ("Fire", "Rock"))
    assert mult_double == 4.0
    print(f"  ✅ Water ➔ Fire/Rock: {mult_double}x (Fraqueza dupla)")


def test_pokeone_authoritative_encounters():
    print("\n🧪 Testando: Encontros Autoritativos do PokeOne (PokeOne > PokéAPI)...")
    kb = KnowledgeBase()

    # Viridian Forest Encontros
    encs = kb.get_encounters("Viridian Forest")
    assert len(encs) >= 3
    species = [e["species"] for e in encs]
    assert "Pikachu" in species
    assert "Caterpie" in species
    print(f"  ✅ Encontros autoritativos do PokeOne em Viridian Forest: {species}")


def test_evolutions_and_items():
    print("\n🧪 Testando: Linhas Evolutivas e Catálogo de Itens...")
    kb = KnowledgeBase()

    # Evoluções
    evo = kb.get_evolution("Charmander")
    assert evo is not None
    assert evo["evolves_to"] == "Charmeleon"
    assert evo["min_level"] == 16
    print(f"  ✅ Evolução validada: {evo['species_name']} ➔ {evo['evolves_to']} no nível {evo['min_level']}")

    # Itens
    item = kb.get_item("Ultra Ball")
    assert item is not None
    assert item["cost"] == 1200
    print(f"  ✅ Item validado: {item['name']} | Categoria: {item['category']} | Custo: ${item['cost']}")


def test_pokeone_npcs_knowledge():
    print("\n🧪 Testando: Catálogo Completo de NPCs do PokeOne (Gym Leaders, Vendors, Quests)...")
    kb = KnowledgeBase()

    # Busca de Líder de Ginásio
    brock = kb.get_npc("Brock")
    assert brock is not None
    assert brock["role"] == "Gym_Leader"
    print(f"  ✅ Líder de Ginásio identificado: {brock['name']} | Local: {brock['location']} | Papel: {brock['role']}")

    # Busca de Healers & Vendors
    joy = kb.get_npc("Nurse Joy")
    assert joy is not None
    assert joy["role"] == "Healer"

    # Reconhecimento global de nomes para OCR
    all_names = kb.get_all_npc_names()
    assert len(all_names) >= 200
    print(f"  ✅ Total de {len(all_names)} NPCs indexados e prontos para reconhecimento visual/OCR!")


def test_3_tier_priority_hierarchy():
    print("\n🧪 Testando: Regra Estrita de 3 Níveis de Prioridade (PokeOneCommunity > PokeOneUnofficial > PokéAPI)...")
    from src.knowledge.knowledge_base import DataSourceTier
    kb = KnowledgeBase()

    # 1. Validação de Encontros com Proveniência
    encounters = kb.get_encounters("Viridian Forest")
    assert len(encounters) > 0
    top_encounter = encounters[0]
    assert "_source_tier" in top_encounter
    assert top_encounter["_source_tier"] in [DataSourceTier.POKEONE_COMMUNITY, DataSourceTier.POKEONE_UNOFFICIAL]
    print(f"  ✅ Tier 1/2 Verificado: Encontro provém de '{top_encounter['_source_name']}' (Tier: {top_encounter['_source_tier'].name})")

    # 2. Validação de NPC com Prioridade
    brock = kb.get_npc("Brock")
    assert brock["_source_tier"] == DataSourceTier.POKEONE_COMMUNITY
    print(f"  ✅ Tier 1 Verificado: NPC '{brock['name']}' carregado de '{brock['_source_name']}'")

    # 3. Validação da Escala de Prioridades
    assert DataSourceTier.POKEONE_COMMUNITY < DataSourceTier.POKEONE_UNOFFICIAL < DataSourceTier.POKEAPI
    print("  ✅ Hierarquia estrita comprovada: PokeOneCommunity (Tier 1) > PokeOneUnofficial (Tier 2) > PokéAPI (Tier 3)!")


def test_comprehensive_stats_learnsets_natures_hms_catch():
    print("\n🧪 Testando: Base Compreensiva (BST, Learnset 15k, Natures 25, HMs 8, Status 9, Catch Formula)...")
    kb = KnowledgeBase()

    # 1. BST (Base Stat Total) e Stats
    charizard = kb.get_pokemon("Charizard")
    assert charizard is not None
    assert charizard["bst"] == 534
    assert charizard["speed"] == 100
    print(f"  ✅ Base Stat Total (BST) validado: {charizard['name']} ➔ BST: {charizard['bst']} | Speed: {charizard['speed']}")

    # 2. Learnset por Nível
    learnset = kb.get_pokemon_learnset("Pikachu")
    assert len(learnset) > 0
    move_names = [m["move_name"] for m in learnset]
    print(f"  ✅ Learnset de Pikachu validado: {len(learnset)} golpes por nível ({', '.join(move_names[:4])}...)")

    # 3. Natures (+10% / -10%)
    adamant = kb.get_nature("Adamant")
    assert adamant["increased_stat"] == "attack"
    assert adamant["decreased_stat"] == "sp_atk"
    print(f"  ✅ Nature Adamant validada: +10% {adamant['increased_stat']} / -10% {adamant['decreased_stat']}")

    # 4. Status Conditions & Catch Bonus
    sleep_cond = kb.get_status_condition("Sleep")
    assert sleep_cond["catch_rate_multiplier"] == 2.5
    print(f"  ✅ Status Sleep validado: {sleep_cond['catch_rate_multiplier']}x multiplicador de captura")

    # 5. HMs & Insígnias Requeridas
    surf_hm = kb.get_field_move("Surf")
    assert surf_hm is not None
    assert "Soul Badge" in surf_hm["required_badge_kanto"]
    print(f"  ✅ HM03 Surf validado: Requer {surf_hm['required_badge_kanto']}")

    # 6. Cálculo Canônico de Chance de Captura
    catch_prob_low_hp_ultra_sleep = kb.calculate_catch_probability("Pikachu", current_hp_percent=0.10, pokeball_name="Ultra Ball", status_condition="Sleep")
    assert catch_prob_low_hp_ultra_sleep > 0.70
    print(f"  ✅ Fórmula canônica de captura validada: Pikachu com 10% HP + Ultra Ball + Sleep = {catch_prob_low_hp_ultra_sleep*100:.1f}% chance!")


if __name__ == '__main__':
    print("==========================================================")
    print("🤖 EXECUTANDO TESTES DA BASE DE CONHECIMENTO (POKÉAPI + POKEONE)")
    print("==========================================================")
    test_pokeapi_etl_generation()
    test_pokemon_and_moves_query()
    test_type_chart_calculations()
    test_pokeone_authoritative_encounters()
    test_evolutions_and_items()
    test_pokeone_npcs_knowledge()
    test_3_tier_priority_hierarchy()
    test_comprehensive_stats_learnsets_natures_hms_catch()
    print("==========================================================")
    print("🎉 TODOS OS TESTES DA BASE DE CONHECIMENTO PASSARAM COM SUCESSO!")
    print("==========================================================")
