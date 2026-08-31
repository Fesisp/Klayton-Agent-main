# Klayton Companion Agent 2.0 - Documentação Principal

## 🤝 Sobre o Klayton 2.0

O **Klayton 2.0** é um **Companion Agent (Agente Companheiro Autônomo e Social)** de elite projetado para operar no MMO PokeOne.

Diferente de bots tradicionais baseados em máquinas de estado rígidas ou loops de if-else, o Klayton opera como um organismo operacional dinâmico acionado por **Utility AI**, **Goal-Oriented Action Planning (GOAP)** com busca $A^*$, **Inteligência Visual Semântica (VLM / Gemini 2.5 Flash / Qwen2.5-VL)**, **Autonomous Learning System (Aprendizado Auto-Supervisionado por Hipóteses)**, **Memória Tríplice Persistente**, escuta de **voz ao vivo (VoiceListener)** e **sintetizador nativo (TTS)**.

---

## 🏛️ Arquitetura Cognitiva Unificada em 6 Camadas

```text
                           FAST PERCEPTION (OpenCV / OCR / Templates)
                                       │
                                       ├──────────► SEMANTIC VISION (Gemini 2.5 Flash / VLM)
                                       │                 (Hypothesis Generation)
                                       ▼
                             PerceptionSnapshot DTO
                                       │
                                       ▼
                                 ┌───────────┐
                                 │WorldState │ (Fonte Única da Verdade / Integridade Epistêmica)
                                 └─────┬─────┘
                                       │
           ┌───────────────────────────┼───────────────────────────┐
           │                           │                           │
     MemorySystem                RelationshipState           LearningEngine
(recall_for_decision)         (Liderança do Felipe)    (SQLite KnowledgeBase / SAFE Tests)
           │                           │                           │
           └───────────────────────────┼───────────────────────────┘
                                       ▼
                                Goal Candidates
                                       │
                                       ▼
                                 UtilityEngine
                         (utility = reward - risk - cost - time)
                         (Direto para DIRECT_COMMAND priority >= 2.0)
                                       │
                                       ▼
                                 GoalInstance
                             (target + target_level + location_hint + constraints)
                                       │
                                       ▼
                                  GOAP Planner
                            (A* State-Space Plan com símbolos reais)
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

## 👁️ Subsistema de Inteligência Visual Semântica (`src/perception/semantic/`)

A percepção semântica atua como **professora visual**, raciocinando sobre cenas inéditas e gerando hipóteses sem controlar diretamente as decisões de baixo nível:

- **`VisualReasoner`**: Orquestrador das 6 camadas da hierarquia perceptual (Determinístico ➔ Modelo Local ➔ Memória/Cache ➔ VLM ➔ Hipótese ➔ Validação).
- **`GeminiVisionProvider`**: Suporte nativo ao `gemini-2.5-flash` via SDK oficial `google-genai` e REST API fallback com schema JSON estruturado.
- **`LocalVisionProvider`**: Suporte a `Qwen2.5-VL-7B-Instruct` via Ollama local.
- **`ConfidenceRouter` & `SemanticBudget`**: Roteia chamadas apenas quando `fast_confidence < 0.55` ou em eventos críticos (`UNKNOWN_SCENE`, `PLAYER_LOST`). Limite de 8 req/min, cooldown de 2.0s e cache por perceptual hash (30s).
- **`PerceptionFusion`**: Fusão de fontes ponderada por confiança (Fast Perception prevalece se confiável; VLM entra quando incerto).
- **`TargetTracker`**: Rastreamento egocêntrico centrado na tela `(0.5, 0.5)` com tolerância a oclusões (0–500ms ➔ 2.0s ➔ 5.0s target lost).
- **`InteractionNavigator`**: Cálculo de vetores de aproximação `(dx, dy)` e confirmação obrigatória de efeito pós-interação (diálogo, menu ou mapa alterado).

---

## 🧠 Autonomous Learning System (`src/learning/`)

Aprendizado auto-supervisionado orientado a: `OBSERVAR ➔ HIPÓTESE ➔ TESTE SAFE ➔ EXECUTAR ➔ OBSERVAR CONSEQÜÊNCIA ➔ CONFIRMAR/REFUTAR ➔ SQLITE KNOWLEDGE BASE`

- **`LearnedFact` & `KnowledgeStatus`**: Transição probabilística de maturidade (`UNKNOWN` ➔ `HYPOTHESIS` ➔ `LIKELY` ➔ `CONFIRMED` ➔ `TRUSTED` / `REFUTED`).
- **Trava de Risco (`ExplorationRisk`)**: Autorização autônoma **apenas para a categoria `SAFE`** (andar, aproximar, examinar objeto, abrir diálogo). Ações `MODERATE` ou `DANGEROUS` (compras, descartes, trocas) são bloqueadas para segurança.
- **`HypothesisEngine`**: Converte hipóteses semânticas em planos `LearningTest` executáveis.
- **`ExperienceValidator`**: Validador soberano de chão de fábrica pelo ambiente (`map_changed`, `dialog_opened`, `movement_success`, `battle_started`).
- **`ConfidenceUpdater`**: Atualização bayesiana com peso de evidência (`evidence_strength`).
- **`KnowledgeBase`**: Repositório SQLite (`data/learning/knowledge.db`) contendo tabelas `learned_facts`, `learning_events`, `decisions`, `observations` e `visual_examples` para reutilização local instantânea.
- **`LearningEngine`**: Orquestrador do ciclo completo e cálculo de métricas automáticas (`False Learning Rate`, `Knowledge Reuse Rate`, `API Dependency`).

---

## 🗄️ Base de Conhecimento SQLite (3 Níveis de Prioridade)

O Klayton gerencia bancos de dados SQLite locais indexados com microsegundos de tempo de resposta via `@lru_cache`, unificando a consulta entre `PokemonDatabase` e `KnowledgeBase`:

### Diretório `data/knowledge/`:

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

### Diretório `data/learning/`:
- **`knowledge.db`**: Banco SQLite para persistência do Aprendizado Auto-Supervisionado.

### Diretório `data/`:
- **`pokedex.db`**: Banco SQLite legado com fallback soberano automático para `data/knowledge/pokemon.sqlite`.

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

## ⚙️ Configuração Modular

O projeto conta com uma estrutura centralizada e dividida em `config/`:
- `config/agent.yaml`: Parâmetros gerais do companheiro.
- `config/voice.yaml`: Voz nativa TTS e microfone.
- `config/perception.yaml`: Limiares de confiança, OCR e bloco `semantic_ai` (Gemini 2.5 Flash / Qwen local).
- `config/navigation.yaml`: Grafo e verificação local.
- `config/battle.yaml`: Trocas defensivas e captura.

---

## 🚀 Como Executar

```bash
# Executar o Runtime Unificado do Klayton Companion Agent 2.0
python run_bot.py
```

### Execução da Suíte Completa de Testes Automatizados:

```bash
python test_integrity.py
python tests/test_autonomous_learning_system.py
python tests/test_self_supervised_learning.py
python tests/test_semantic_vision.py
python tests/test_perception_manager.py
python tests/test_e2e_real_goap_pipeline.py
python tests/test_e2e_goal_instance_pipeline.py
python tests/test_world_state_sync.py
python tests/test_goap_and_utility_ai.py
python tests/test_companion_agent_100_percent.py
python tests/test_pokeapi_knowledge_base.py
```
