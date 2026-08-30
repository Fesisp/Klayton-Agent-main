# Klayton Companion Agent 2.0 - Technical Architecture & Developer Guide

Este documento detalha a arquitetura interna do **Klayton Companion Agent 2.0**, estruturada em um **Framework de Agente Autônomo e Social de Segunda Pessoa (Companion Agent)**.

---

## 🏛️ Estrutura de Diretórios & Módulos

```
src/
├── agent/
│   ├── agent.py                 # Core KlaytonAgent desacoplado
│   ├── companion_agent.py       # Container do Agente Companheiro Social
│   └── goal_manager.py          # Conciliação de Metas Compartilhadas vs Pessoais
├── cognition/
│   ├── intent_parser.py         # Processador de intenções em linguagem natural
│   ├── personality.py           # Matriz de personalidade (Curiosidade, Risco, Independência)
│   ├── relationship.py          # Contexto social de relacionamento (Líder, Distância, Instruções)
│   └── shared_attention.py      # Resolução de referências contextuais ("Pega esse")
├── core/
│   ├── event_bus.py             # Barramento de eventos desacoplado Pub/Sub
│   ├── watchdog.py              # Supervisor anti-loop e anti-estagnação (AgentWatchdog)
│   ├── hotkey_listener.py       # Listener de atalhos globais
│   └── udp_receiver.py          # Servidor UDP para controle remoto
├── decision/
│   ├── goal_engine.py           # Motor de metas (Goal Enum)
│   ├── goap_planner.py          # Planejador GOAP com suporte a REPLAN dinâmico
│   ├── utility_engine.py        # Utility AI (utility = reward - risk - cost - time)
│   └── battle_strategy.py       # Motor tático de batalha v2.5
├── interaction/
│   ├── dialogue_manager.py      # Thought -> Action -> Speech com TTS local
│   └── clarification_engine.py  # Gerador de perguntas de esclarecimento
├── memory/
│   └── agent_memory.py          # Memória em 3 camadas (Working, Episodic, Semantic)
├── navigation/
│   ├── map_graph.py             # Grafo de conexão entre mapas e roteamento A*
│   └── movement_verifier.py     # Verificador contínuo de movimento ("Never Trust Last Action")
├── perception/
│   ├── observation.py           # Percepção tipada com índice de confiança (confidence >= 0.50)
│   ├── game_state_detector.py   # Detecção de estados de jogo
│   ├── chat_handler.py          # Detecção de PM e segurança
│   ├── ocr_engine.py            # Reconhecimento OCR
│   └── screen_capture.py        # Captura de tela ultra-rápida (MSS)
├── skills/
│   ├── base_skill.py            # Interface genérica de Skill
│   ├── battle_skill.py          # Habilidade de combate
│   └── hunting_skill.py         # Habilidade de caça e movimentação
├── tools/
│   └── replay_logger.py         # Gravador de sessões e decisões em JSONL
└── world/
    └── world_state.py           # Modelo unificado do mundo (Single Source of Truth)
```

---

## 💡 Fluxo Cognitivo Continuo

1. **Perception**: A visão computacional e OCR alimentam o `WorldState`, gerando objetos `Observation` com `confidence`.
2. **Cognition**: O `RelationshipState` avalia a distância e postura com o líder ("Felipe"). A `Personality` ajusta os modificadores de atratividade das ações.
3. **Agency**: O `CompanionGoalManager` escolhe o sub-objetivo ativo. O `GOAPPlanner` encontra a melhor fila de *Skills*. Se o HP ou o ambiente mudarem, o `REPLAN` é acionado imediatamente.
4. **Interaction**: O `DialogueManager` verbaliza intenções públicas (*"Vou no Pokémon Center e já volto!"*) enquanto a *Skill* ativa envia entradas de baixo nível ao jogo.

---

## 🧪 Testes Automatizados & Verificação

A suíte de testes de integridade pode ser executada a qualquer momento:
```bash
python test_integrity.py
```
Ou testando os submódulos individualmente:
- `scratch/test_phase1.py` (WorldState & EventBus)
- `scratch/test_goal_engine.py` (Goal Engine)
- `scratch/test_agent_2_0.py` (Autonomous Agent)
- `scratch/test_companion_agent.py` (Companion Agent & Diálogo)
- `scratch/test_hardening.py` (Navegação, Watchdog, Replay & Confiança)
