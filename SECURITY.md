# Security Policy — Klayton Agent 2.0 / 2.1

Data: 2026-08-31  
Versão: 2.1.0

---

## 🔒 Políticas de Segurança e Isolamento

1. **Privacidade de Dados de Percepção**: Imagens, frames de percepção visual e bancos SQLite permanecem 100% locais no diretório `data/`. Nenhum dado bruto é transmitido externamente a menos que configurado explicitamente via VLM.
2. **Proteção de Credenciais e Segredos**: Chaves de API (ex: OpenAI, provedores LLM/VLM) são carregadas estritamente via variáveis de ambiente (`.env`) pelo `CredentialsManager` e mascaradas em logs.
3. **Operação 100% Out-of-Process (Zero-Injection)**: O agente opera em processo isolado utilizando exclusivamente APIs padrão de sistema operacional (Win32 Desktop Capture e Virtual Key Events). É expressamente proibida a injeção de DLLs ou modificação de memória de terceiros (`ReadProcessMemory`/`WriteProcessMemory`).
4. **Criptografia de Comunicações**: Conexões de rede externas aplicam TLS 1.3/HTTPS rigoroso.
