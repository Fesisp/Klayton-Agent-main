# Guia do Desenvolvedor - Klayton Agent 2.0

Data: 2026-08-31  
Versão: 2.0.0

---

## 🏗️ Arquitetura Interna e Fronteiras de Módulos

1. **`src/world/world_state.py`**: Fonte única da verdade. Todas as alterações devem ocorrer via chamadas aos métodos `update_*()` para atualizar a marcação temporal e incrementar a versão (`world.version`).
2. **`src/decision/`**: `GoalArbitrator`, `GOAPPlanner` e `UtilityAI`. O planejador opera em leituras do `WorldState` sem modificar estado global diretamente.
3. **`src/execution/`**: `ExecutionCoordinator` gerencia o ciclo de vida das `BaseSkill` mantendo o estado `SkillStatus.RUNNING` durante tarefas de múltiplos ticks.
4. **`src/memory/runtime/`**: `MemoryFacade` expõe a camada de persistência com `EvidenceSource` e política de admissão baseada em tripla confirmação idêntica.
5. **`src/runtime/`**: `RuntimeSupervisor` supervisiona heartbeats (`Watchdog`), limites de frequência (`RuntimeScheduler`), isolamento de falhas (`CircuitBreaker`) e guarda de segurança de inputs (`InputGuard`).

---

## 🧪 Suíte de Testes e Validação
Para rodar a verificação completa de release antes de comitar:
```bash
python tools/verify.py --release
```
