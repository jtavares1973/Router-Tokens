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
