# CHANGELOG - Klayton Agent 2.0

## [2.0.0] - 2026-08-31

### Added (Adicionado)
- **Motor de Autonomia de Metas (Etapa 6)**: `GoalStack`, `GoalArbitrator`, `LongHorizonPlanner`, `TaskGraph`, `GoalProgressEvaluator` e `LoopDetector`.
- **Memória Persistente & Aprendizado (Etapa 7)**: `MemoryStore` SQLite, `MemoryRecord` com proveniência (`EvidenceSource`), `MemoryAdmissionPolicy` (trava de segurança de 3 confirmações idênticas), `ContradictionResolver` (`superseded_by`) e `MemoryDecay`.
- **Inteligência Social & Orientação Humana (Etapa 8)**: `ContextResolver`, `AmbiguityResolver`, `CommandRouter`, `ExplanationEngine` baseado em estado real e `TeachingInterpreter`.
- **Orquestração e Segurança de Runtime (Etapa 9)**: `RuntimeSupervisor`, `FaultManager`, `ShutdownManager`, `InputGuard` (Parada de Emergência `Ctrl+Shift+F12`), `Watchdog`, `StateGuard` (versionamento `world.version`) e `CircuitBreaker`.
- **Qualidade de Release e Verificação (Etapa 10)**: `version.py`, `RELEASE_MANIFEST.json`, `tools/check_environment.py`, `tools/benchmark.py`, `tools/release_audit.py`, `tools/build_release.py` e suporte ao modo `--release` no `tools/verify.py`.

### Changed (Alterado)
- Removidos todos os caminhos absolutos hardcoded locais em favor de resolução dinâmica via `Path(__file__)`.
- Consolidado o contrato de `WorldState` como fonte única e imutável da verdade com suporte a versionamento atômico.
