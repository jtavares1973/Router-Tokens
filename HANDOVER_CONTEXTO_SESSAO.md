# HANDOVER DE CONTEXTO DA SESSÃO — PROJETO `Router-Tokens`

**Última Atualização:** 20/10/2026 às 17:17 (Horário de Brasília)  
**Estação:** `ZAMORA` (AMD Ryzen 9 7950X | NVIDIA GeForce RTX 5090 32 GB GDDR7 | 64 GB RAM)  
**Status Global:** **VERSÃO 1.3 HOMOLOGADA E SELADA (OPUS 5.5) — CACHE LRU DETERMINÍSTICO (0 ms) + BATCHING CONCORRENTE (223 ms/end) + MODELO RESIDENTE (keep_alive=-1) + 23/23 TESTES PASSED**

---

## 1. As 4 Otimizações Estratégicas da Versão 1.3 (Homologadas pelo Opus 5.5)

1. **Modelo Residente Permanente (`keep_alive: -1`):**
   - Configurado `"keep_alive": -1` nas chamadas ao Ollama na RTX 5090;
   - Elimina o descarte a cada 5 minutos e zera os picos de carregamento (*cold start*) do barramento PCIe.
2. **Cache LRU Determinístico em Memória no GEV-Lite:**
   - Dicionário com limite de 1.024 entradas indexado por hash SHA-256 (`pergunta + opções + contexto`);
   - Consultas repetidas retornam instantaneamente em **0 ms** (`modo_sistema: "cache_lru_fast_gate"`).
3. **Processamento em Lote Concorrente (*Batching* para ETL):**
   - Nova função aditiva [`rotear_lote_instrucoes()`](file:///d:/___SCRIPT/Router-Tokens/router_tokens.py);
   - Processamento concorrente saturando os multiprocessadores da RTX 5090, reduzindo o tempo por endereço para **223,8 ms** (mais que o dobro de vazão).
4. **Métrica Nativa de Primeira Passagem:**
   - Campo canônico `aprovado_primeira: bool` integrado ao [`ResultadoRoteamento`](file:///d:/___SCRIPT/Router-Tokens/router_tokens.py) e ao log de auditoria.

---

## 2. A Tríade Canônica de Benchmarks Homologados (Zero Regressão)

1. **Benchmark 1 — Pytest Expandido com 23 Testes ([`test_bateria_completa_router.py`](file:///d:/___SCRIPT/Router-Tokens/test_bateria_completa_router.py)):**
   - **Resultado:** **23/23 APROVADOS (100% PASSED)**;
   - Novos testes:
     * `test_21_cache_lru_gev_lite_instantaneo`: PASSED (0 ms);
     * `test_22_batching_concorrente_preserva_ordem_e_fiscal`: PASSED;
     * `test_23_metrica_nativa_aprovado_primeira`: PASSED.

2. **Benchmark 2 — RouterEval Acadêmico MilkThink-Lab ([`benchmark_routereval_zamora.py`](file:///d:/___SCRIPT/Router-Tokens/benchmark_routereval_zamora.py)):**
   - **Resultado:** **16/16 APROVADOS (100% PASSED em 0.8s)**;
   - Retenção de Desempenho ($V_r$): **`1.0000`**;
   - Eficiência Econômica ($E_p$): **`72,5%` de economia**;
   - Over-Routing = `0,0%` | Under-Routing = `0,0%`.

3. **Benchmark 3 — Promptfoo via LiteLLM Proxy Porta 4000 ([`promptfooconfig.yaml`](file:///d:/___SCRIPT/Router-Tokens/promptfooconfig.yaml)):**
   - **Resultado:** **10/10 APROVADOS (100% PASSED em 12 segundos)**.

---

## 3. Telemetria e Prova Real da Versão 1.3

* **Lote de Endereços do DF Concorrente:** 5 endereços processados em **1.119 ms** (média de **223,8 ms** por endereço);
* **Aprovação de Primeira Passagem:** **100%** de acerto retido no Degrau 1 (RTX 5090 local a custo zero);
* **Telemetria de Hardware:** 48°C | 36,6W | 24 GB de VRAM livres;
* **Chancela de Governança:** Homologação pericial plena pelo Auditor Chefe Opus 5.5 e Orquestrador Chefe Argon.


---

## Laudo de Sessão — 21/10/2026 (Auditoria do Antigravity e Variáveis do Windows)

**Diagnóstico:** Windows saudável (SSD Corsair MP700 Elite "Healthy", PATH sem duplicatas). Não há necessidade de reinstalação.

**Causas encontradas:**
- Pasta `_teste_litellm_isolado` apagada → MCP `litellm-executor` quebrado.
- 4 desligamentos inesperados (Kernel-Power 41): 11/10 15:26, 13/10 22:40, 17/10 17:01 e 17/10 22:24. Suspeita de energia/travamento (verificar cabo 12V-2x6 / fonte se repetir).
- 7 quedas do language_server do Antigravity (14/10 a 21/10).
- 8 falhas do WSLService por tempo esgotado (afeta `agentmemory`).
- Ollama alertava biblioteca incompatível `ggml-base.dll` do llama.cpp (WinGet) no PATH.

**Correções aplicadas:**
1. `mcp_config.json`: `litellm-executor` com `"disabled": true` (backup `mcp_config.json.bak_20261021`).
2. Plugin `science` (40 skills) desativado via `JetboxWriteState`.
3. Variável de usuário `PYTHONUTF8=1` criada.
4. GitHub CLI instalado (`gh version 2.102.1`). Pendente: `gh auth login`.
5. Pasta do llama.cpp removida do PATH do usuário (20 → 19 entradas; backup em `_entrega/backup_PATH_usuario_20261021.txt`).
6. Ollama (11434) e LiteLLM (4000) religados via WMI (`Win32_Process.Create`) — processos lançados pelo terminal do agente morrem ao fim do comando. Prova: 8 modelos no proxy; `zamora-executor-7b` respondeu "OK" em 2.470 ms.

**Pendência exata para o próximo turno:** após reiniciar o Antigravity, conferir se `notebooks`, `visualization` e `data-agent-kit` sobem; confirmar `gh auth status`.

**Complemento 21/10 (restabelecimento do ambiente):**
- Bancos são contêineres Docker: `dev-postgres` (postgis 17-3.5, porta 5432) estava parado desde 24/09 (código 255, desligamento brusco) — religado, recuperação automática do PostgreSQL OK, política alterada de `no` para `unless-stopped`. `dev-sqlserver` (porta 1433) já era `unless-stopped`. Prova via MCP: `devdb` com PostGIS e 40 tabelas; SQL Server com banco `ARCGIS`.
- Ollama e LiteLLM não tinham inicialização automática (causa de ficarem fora após cada queda). Criados atalhos na pasta Inicializar: `Ollama.lnk` e `ZAMORA LiteLLM Proxy 4000.lnk` (minimizado).
- Fonte do PC é de 850 W — principal suspeita das 10 quedas abruptas (RTX 5090 575 W + 7950X 230 W). Investigação de hardware adiada a pedido do usuário.
- MCP `notebooks`/`visualization`/`data-agent-kit` usam argumentos `*-antigravityide` (extensão da IDE antiga) e não sobem no Antigravity 2.24.

**Complemento 21/10 11:32 (GitHub CLI):**
- `gh auth login` concluído pelo fluxo de código no navegador. Prova: `gh auth status` → conta `jtavares1973` (keyring), protocolo https, escopos `gist`, `read:org`, `repo`; `gh api user` respondeu `jtavares1973`.
- O terminal do agente ainda não encontra `gh` pelo nome (o processo do Antigravity foi aberto antes da mudança no PATH). Até reiniciar a IDE, use o caminho completo `C:\Program Files\GitHub CLI\gh.exe`.
- **Pendência:** reiniciar o Antigravity por completo e confirmar que `gh --version` funciona pelo nome.
