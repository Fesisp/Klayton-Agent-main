# Compliance & Human-Supervision Mode — Klayton 2.1

Data: 2026-08-31  
Versão: 2.1.0 (Compliance & Human-Supervision Mode)

---

## 🏛️ Filosofia e Princípios de Compliance

O módulo de compliance do Klayton 2.1 foi projetado para assegurar **operação segura, auditável, previsível e supervisionável** do agente, sem recorrer a técnicas de evasão de anti-bot ou falsificação de padrões.

### O que o sistema NÃO faz:
- Não falsifica identidade nem altera fingerprints de processo/janela.
- Não injeta atrasos aleatórios destinados a iludir mecanismos de detecção.
- Não reage ou tenta burlar verificações de CAPTCHA ou anti-cheat.

### O que o sistema FAZ:
- **Limite Estrito de Taxa (`ActionRateLimiter`)**: Restringe fisicamente os acionamentos a no máximo 8 ações/segundo.
- **Limite de Duração de Sessão (`SessionGuard`)**: Pausa automaticamente após 60 minutos de execução contínua, exigindo confirmação humana para continuar.
- **Detecção de Loops Improdutivos (`RepetitiveBehaviorGuard`)**: Interrompe repetições da mesma ação se não houver avanço no estado do mundo (`world.version`).
- **Validação de Janela em Foco (`SupervisionGate`)**: Bloqueia o envio de inputs se a janela alvo do jogo perder o foco.
- **Pausa em Confiança Baixa (`minimum_world_confidence = 0.70`)**: Suspende ações complexas quando a certeza da percepção do mundo cair abaixo de 70%.
- **Parada de Emergência Prioritária (`Ctrl+Shift+F12`)**: Solta imediatamente todas as teclas e cancela a fila de ações.
