# Guia do Operador - Klayton Agent 2.0

Data: 2026-08-31  
Versão: 2.0.0

---

## 🚀 Como Executar e Operar o Agente

### 1. Requisitos de Ambiente
- Sistema Operacional: Windows 10/11
- Python 3.11+
- Dependências instaladas via `pip install -r requirements-lock.txt`

### 2. Verificação de Integridade Pré-Execução
Antes de iniciar a sessão do agente, execute o Quality Gate de ambiente:
```bash
python tools/check_environment.py
```

### 3. Controles Principais e Segurança
- **Parada de Emergência (Emergency Stop)**: Pressione `Ctrl+Shift+F12` a qualquer momento para liberar imediatamente todas as teclas e pausar o runtime.
- **Pausa Conversacional**: Envie o comando de voz ou texto `"pausa"` ou `"pause"` para suspender novas ações físicas sem perder metas ou estado.
- **Solicitação de Explicação**: Pergunte `"por que você fez isso?"` para receber a fundamentação da decisão baseada exclusivamente no estado atual.
