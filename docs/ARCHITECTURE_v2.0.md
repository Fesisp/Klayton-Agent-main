# Visão Geral da Arquitetura Klayton 2.0 (ARCHITECTURE_v2.0.md)

## 🤝 Filosofia do Klayton 2.0

O Klayton 2.0 foi desenhado para ser um **Agente Companheiro Autônomo e Social**. Ele combina percepção multimodal, raciocínio em tempo real, memória de aprendizado e voz para pair-playing em MMO.

---

## 🏛️ Fluxo de Dados e Tomada de Decisão (Cadeia de 5 Camadas)

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

## 📚 Módulos Principais

1. **`KlaytonCompanionAgent`** ([`src/agent/companion_agent.py`](file:///c:/Users/mrfel/OneDrive/Laboratorio/Developer/Klayton-Agent-main/src/agent/companion_agent.py)): Cérebro central do runtime.
2. **`WorldState`** ([`src/world/world_state.py`](file:///c:/Users/mrfel/OneDrive/Laboratorio/Developer/Klayton-Agent-main/src/world/world_state.py)): Single Source of Truth que armazena estado de combate, jogador, localização, recursos, missões e companheiro.
3. **`UtilityEngine`** ([`src/decision/utility_engine.py`](file:///c:/Users/mrfel/OneDrive/Laboratorio/Developer/Klayton-Agent-main/src/decision/utility_engine.py)): Pontuador racional de metas via $\text{utility} = \text{reward} - \text{risk} - \text{cost} - \text{time}$.
4. **`GOAPPlanner`** ([`src/decision/goap_planner.py`](file:///c:/Users/mrfel/OneDrive/Laboratorio/Developer/Klayton-Agent-main/src/decision/goap_planner.py)): Planejador por busca $A^*$ no espaço de estados com pilha de interrupção e retomada (*Resume Stack*).
5. **`GoalInstance`** ([`src/decision/goal_engine.py`](file:///c:/Users/mrfel/OneDrive/Laboratorio/Developer/Klayton-Agent-main/src/decision/goal_engine.py)): Instância parametrizada de objetivo contendo alvos (`target`), restrições (`constraints`) e critérios de conclusão.
6. **`KnowledgeBase`** ([`src/knowledge/knowledge_base.py`](file:///c:/Users/mrfel/OneDrive/Laboratorio/Developer/Klayton-Agent-main/src/knowledge/knowledge_base.py)): Base SQLite em 3 níveis ($\text{PokeOneCommunity} \succ \text{PokeOneUnofficial} \succ \text{PokéAPI}$).
7. **`MemorySystem`** ([`src/cognition/memory_system.py`](file:///c:/Users/mrfel/OneDrive/Laboratorio/Developer/Klayton-Agent-main/src/cognition/memory_system.py)): Memória tríplice persistente (Working, Episodic, Semantic) que registra eficiências de XP/h e orienta a escolha de rotas.
