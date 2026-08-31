# Threat Model — Klayton Agent 2.0 / 2.1 (Adaptado do Projeto Interview)

Data: 2026-08-31  
Versão: 2.1.0

---

## 🎯 Ativos Protegidos (Assets)
- Chaves de API e Segredos de Integração.
- Bancos de Dados de Conhecimento e Memória Persistente SQLite (`data/`).
- Integridade do Sistema Operacional e Fila de Inputs Físicos.

---

## 🛡️ Vetores de Ameaça e Mitigações

| Vetor de Ameaça | Mitigação Aplicada |
| :--- | :--- |
| **Vazamento de Chaves de API em Logs** | Carregamento via `CredentialsManager` com mascaramento de segredos (`mask_secret`). |
| **Interferência ou Injeção de Código em Processos Externos** | Operação 100% Out-of-Process (`ProcessIsolationGuard`) via APIs padrão de SO. Zero DLL Injection / Zero Memory Hooking. |
| **Spam de Inputs ou Teclas Presas** | `InputGuard` com limite de taxa (8 acionamentos/s) e Parada de Emergência `Ctrl+Shift+F12`. |
| **Corrupção de Memória Persistente** | Transações SQLite atômicas e barramento de eventos monotônico (`EventBus`). |
