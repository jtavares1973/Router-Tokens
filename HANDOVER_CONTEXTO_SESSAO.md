# HANDOVER DE CONTEXTO DA SESSÃO — PROJETO `Router-Tokens`

**Última Atualização:** 20/10/2026 às 11:21 (Horário de Brasília)  
**Estação:** `ZAMORA` (AMD Ryzen 9 7950X | NVIDIA GeForce RTX 5090 32 GB GDDR7 | 64 GB RAM)  
**Status Global:** **VERSÃO 1.0 CANÔNICA CONCLUÍDA — INSTITUCIONALIZADA COMO REGRA GLOBAL PERMANENTE + TRÍADE DE HOMOLOGAÇÃO 100% PRESERVADA (ZERO REGRESSÃO)**

---

## 1. A Tríade Canônica de Benchmarks Homologados

1. **Benchmark 1 — Promptfoo via LiteLLM Proxy Porta 4000 ([`promptfooconfig.yaml`](file:///d:/___SCRIPT/Router-Tokens/promptfooconfig.yaml)):**
   - **Resultado:** **10/10 APROVADOS (100% PASSED em 12 segundos)**;
   - Avaliação da RTX 5090 local (modelos Qwen 32B e 7B) em código puro, assert e travas anti-piora a custo zero;
   - Relatório: [`_entrega/promptfoo_resultado.json`](file:///d:/___SCRIPT/Router-Tokens/_entrega/promptfoo_resultado.json).

2. **Benchmark 2 — RouterEval Acadêmico MilkThink-Lab ([`benchmark_routereval_zamora.py`](file:///d:/___SCRIPT/Router-Tokens/benchmark_routereval_zamora.py)):**
   - **Resultado:** **16/16 APROVADOS (100% PASSED)**;
   - Índice de Retenção de Desempenho ($V_r$): **`1.0000`** (paridade perfeita com Oráculo de alto custo);
   - Eficiência Econômica ($E_p$): **`72,5%` de economia** ponderada;
   - Over-Routing (Desperdício) = **`0,0%`** | Under-Routing (Sub-capacidade) = **`0,0%`**;
   - Relatório: [`_entrega/router_eval_benchmark.json`](file:///d:/___SCRIPT/Router-Tokens/_entrega/router_eval_benchmark.json).

3. **Benchmark 3 — Promptfoo com Wrapper do Roteador ([`promptfooconfig_router.yaml`](file:///d:/___SCRIPT/Router-Tokens/promptfooconfig_router.yaml) + [`router_target.py`](file:///d:/___SCRIPT/Router-Tokens/router_target.py)):**
   - **Resultado:** **4/4 APROVADOS (100% PASSED em 18 segundos)**;
   - Validação direta das decisões de metadados em JavaScript no Promptfoo:
     * Tarefa de 1 arquivo -> Despachada para `local_gpu` (`economizou_nuvem = true`) (**PASS**);
     * Tarefa de 3 arquivos -> Despachada para `antigravity_fast` (**PASS**);
     * Tarefa de 6 arquivos -> Despachada para `antigravity_cloud` com `gemini-4-argon` (**PASS**);
     * Algoritmo de 2 arquivos -> Despachado para `agentic_deepseek` (**PASS**);
   - Relatório: [`_entrega/promptfoo_router_resultado.json`](file:///d:/___SCRIPT/Router-Tokens/_entrega/promptfoo_router_resultado.json).

---

## 2. Expansão Cognitiva na RTX 5090 (Modelo Raciocinador Integrado)

- **Novo Modelo Local Ingerido:** `deepseek-r1:32b` (19 GB, destilação oficial no backbone Qwen-32B com raciocínio profundo);
- **Desafio Pericial de Lógica:** Reconciliação com janela deslizante temporal e desempate por menor $\Delta t$ ([`teste_comparativo_raciocinio.py`](file:///d:/___SCRIPT/Router-Tokens/teste_comparativo_raciocinio.py));
- **Telemetria de Inferência na RTX 5090:**
  * **Velocidade de Geração:** **`64.8 tokens/segundo`**;
  * **Profundidade de Pensamento:** **`3.921 caracteres de cadeia de raciocínio (<think>)`** auto-auditando os casos de borda antes de emitir o código;
  * **Confronto Direto:**
    - `qwen2.5-coder:32b`: 8.10s | 39.4 tokens/s | 273 tokens (emissão direta) | AST OK | Asserts 100% OK;
    - `deepseek-r1:32b`: 26.94s | 64.8 tokens/s | 1.111 tokens (planejamento mental completo) | AST OK | Asserts 100% OK;
  * **Relatório:** [`_entrega/comparativo_raciocinio_5090.json`](file:///d:/___SCRIPT/Router-Tokens/_entrega/comparativo_raciocinio_5090.json).
- **Integração no LiteLLM Proxy Porta 4000 ([`litellm_config.yaml`](file:///d:/___SCRIPT/Router-Tokens/litellm_config.yaml)):**
  * Modelo mapeado: `zamora-raciocinador-32b` (com separação automática de `reasoning_content` padrão OpenAI).

---

## 3. Garantia Inviolável de Não-Regressão
- **Suíte Pytest 16/16:** [`test_bateria_completa_router.py`](file:///d:/___SCRIPT/Router-Tokens/test_bateria_completa_router.py) com **`16/16 PASSED em 70.80s`**;
- **RouterEval Acadêmico:** **`16/16 PASSED em 0.8s`**;
- **Etiqueta Git Estável de Referência:** `v1.0-homologacao-triade-estavel` (commit `dab3caf`).

---

## 4. Institucionalização como Regra Global e Portabilidade

1. **Diretriz Canônica Global (`C:\Users\canin\.gemini\GEMINI.md`):**
   - Seção 6 atualizada para incluir a Política 90/10 com o LiteLLM Proxy na porta 4000 e o duplo operário local (Qwen 32B e DeepSeek R1 32B).
2. **Regra Global no Ecossistema (`C:\Users\canin\.gemini\config\rules\politica-90-10-rtx5090-litellm.md`):**
   - Regra universal permanente que orienta todos os agentes e subagentes do Antigravity.
3. **Inicializador de Um Clique:** [`iniciar_zamora.bat`](file:///d:/___SCRIPT/Router-Tokens/iniciar_zamora.bat) para subida imediata do serviço com blindagem UTF-8.
4. **Perfil Portátil do Trabalho (RTX 5070 16 GB):** [`litellm_config_trabalho_16gb.yaml`](file:///d:/___SCRIPT/Router-Tokens/litellm_config_trabalho_16gb.yaml) calibrado para `deepseek-r1:14b` e `qwen2.5-coder:7b`.

---

## 5. Parecer do Orquestrador Chefe (Argon / Opus 5.5)
- Arquitetura de Roteamento Inteligente 90/10 chancelada em nível máximo de maturidade e simplicidade operacional.
