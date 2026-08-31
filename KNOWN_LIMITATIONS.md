# Limitações Conhecidas do Klayton Agent 2.0

Data: 2026-08-31  
Versão: 2.0.0 (Release Candidate 1)

---

## 📌 Limitações Conhecidas de Escopo e Runtime

1. **Plataforma de Execução**: O agente foi desenvolvido e otimizado para o sistema operacional Windows 10/11. A captura de tela e injeção de acionamentos dependem das APIs do Windows (`pywin32` / Win32 API).
2. **Dependência de Resolução de Tela**: A percepção por OCR e padrões de template em combate assume resoluções de tela padrão (16:9 / 1080p).
3. **Visão Multimodal (VLM)**: A integração com provedores VLM externos exige chaves de API válidas no arquivo de configuração. Caso esteja indisponível, o agente opera em modo degradado com percepção determinística local.
4. **Bancos de Dados SQLite de NPCs**: As tabelas de NPCs e encontros do atlas comunitário estão marcadas como parcialmente preenchidas (`PARTIAL`), enquanto tabelas de Pokémon, Golpes, Tipos e Natures estão 100% integradas.
