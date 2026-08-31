# Klayton Companion Agent 2.0 - Documentação Principal

## 🤝 Sobre o Klayton 2.0

O **Klayton 2.0** é um **Companion Agent (Agente Companheiro Autônomo e Social)** de elite projetado para operar no MMO PokeOne.

Diferente de bots tradicionais baseados em máquinas de estado rígidas ou loops de if-else, o Klayton opera como um organismo operacional dinâmico acionado por **Utility AI**, **Goal-Oriented Action Planning (GOAP)** com busca $A^*$, **Memória Tríplice Persistente**, escuta de **voz ao vivo (VoiceListener)** e **sintetizador nativo (TTS)**.

---

## 🏛️ Arquitetura Cognitiva Unificada em 5 Camadas

```
                             PERCEPTION (Visão / OCR)
                                       │
                                       ▼
                                 ┌───────────┐
                                 │WorldState │ (Fonte Única da Verdade)
                                 └─────┬─────┘
                                       │
           ┌───────────────────────────┼───────────────────────────┐
           │                           │                           │
     MemorySystem                RelationshipState           IntentParser
(Record & Statistical Spot)   (Liderança do Felipe)    (Comandos & Target: Pikachu 35)
           │                           │                           │
           └───────────────────────────┼───────────────────────────┘
                                       ▼
                                Goal Candidates
                                       │
                                       ▼
                                 UtilityEngine
                         (utility = reward - risk - cost - time)
                                       │
                                       ▼
                                 GoalInstance
                             (target + constraints)
                                       │
                                       ▼
                                  GOAP Planner
                            (A* State-Space Plan)
                                       │
                                       ▼
                               Hierarchical Planner
                            (Decomposição de Subtarefas)
                                       │
                                       ▼
                                 Master Triad
                     (Navigation + Recovery + 13 Skills)
                                       │
                                       ▼
                                    PokeOne
                                       │
                                       └────────► percepção novamente (Loop Fechado)
```

---

## 🗄️ Base de Conhecimento SQLite (3 Níveis de Prioridade)

O Klayton possui 7 bancos de dados SQLite locais em `data/knowledge/` indexados com microsegundos de tempo de resposta via `@lru_cache`:

| Banco SQLite | Tabela Principal | Total Registros | Atributos Indexados |
| :--- | :--- | :---: | :--- |
| **`pokemon.sqlite`** | `pokemon` | **809 Pokémon** | Stats Totais, **BST (Base Stat Total)**, **Catch Rate (0–255)**, Base XP, Tipos, Altura, Peso |
| **`pokemon.sqlite`** | `pokemon_learnset`| **15.145 Golpes** | Movimentos aprendidos por nível para cada espécie |
| **`moves.sqlite`** | `moves` | **522 Golpes** | Power, Accuracy, PP, Priority, Category (Physical/Special/Status) |
| **`types.sqlite`** | `type_chart` | **324 Combinações** | Matriz $18 \times 18$ de fraquezas, resistências e imunidades |
| **`natures.sqlite`** | `natures` | **25 Naturezas** | Stat aumentado (+10%), Stat reduzido (-10%), Sabores de Berries |
| **`status_conditions.sqlite`** | `status_conditions`| **9 Condições** | Multiplicadores de captura (2.5x Sleep/Freeze, 1.5x Par/Psn/Brn) e penalidades |
| **`hms_field_moves.sqlite`** | `field_moves` | **8 HMs / Campo** | Cut, Surf, Fly, Strength, Flash, Rock Smash, Waterfall, Dive e **insígnias necessárias** |
| **`items.sqlite`** | `items` | **26 Itens** | Pokébolas, Poções, Pedras Evolutivas, Berries e Held Items competitivos |
| **`npcs.sqlite`** | `npcs` | **232 NPCs** | Gym Leaders, Vendedores, Healers, Move Tutors e Quest NPCs do PokeOne |
| **`pokeone_encounters.sqlite`**| `encounters`| **318 Spawns** | Spawns do PokeOne Community Location Atlas com níveis min/max e métodos |

### 👑 Hierarquia de Resolução de Conflitos:
$$\mathbf{1^\circ\ PokeOneCommunity} \succ \mathbf{2^\circ\ PokeOneUnofficial} \succ \mathbf{3^\circ\ Pok\acute{e}API}$$

---

## 🚶 Catálogo das 13 Skills Concretas

- **`FollowSkill`**: Acompanhamento inteligente (aproximação, dead reckoning em perda de visão, troca de mapa e comandos de voz *"vem comigo"*, *"espera aqui"*, *"fica perto"*, *"vai na frente"*).
- **`WaitSkill`**: Espera no local solicitado.
- **`NavigateSkill`**: Condução intermapas via A* e grafo de 355 mapas do PokeOne (Kanto, Sevii Islands 1-7, Johto, Destiny Island, Unova e Eventos).
- **`HealSkill`**: Procedimento autônomo de cura nos Centros Pokémon.
- **`BattleSkill`**: Combate por fraquezas elementares, categorias físicas/especiais e trocas defensivas.
- **`HuntingSkill`**: Patrulhamento da grama alta em vaivém.
- **`CaptureSkill`**: Enfraquecimento seguro e cálculo da fórmula canônica de captura.
- **`FishingSkill`**: Pesca completa (varas, fisgada, duelo).
- **`InteractionSkill`**: Diálogo com NPCs, placas e baús.
- **`ShoppingSkill`**: Compra automática de suprimentos nos Pokemarts.
- **`QuestSkill`**: Progressão de objetivos do `QuestEngine` (ginásios, insígnias, líderes).
- **`ExploreSkill`**: Exploração de áreas não mapeadas.
- **`RecoverSkill`**: Descolamento físico 4-way anti-stuck.

---

## 🚀 Como Executar

```bash
# Executar o Runtime Unificado do Klayton Companion Agent 2.0
python run_bot.py
```

### Execução da Suíte de Testes Automatizados:
```bash
python test_integrity.py
python tests/test_companion_agent_100_percent.py
python tests/test_goap_and_utility_ai.py
python tests/test_pokeapi_knowledge_base.py
```
