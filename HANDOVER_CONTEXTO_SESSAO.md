# HANDOVER DE CONTEXTO DA SESSÃO — PROJETO `Router-Tokens`

**Última Atualização:** 20/10/2026 às 16:18 (Horário de Brasília)  
**Estação:** `ZAMORA` (AMD Ryzen 9 7950X | NVIDIA GeForce RTX 5090 32 GB GDDR7 | 64 GB RAM)  
**Status Global:** **VERSÃO 1.1 HOMOLOGADA (ARGON + OPUS 5.5) — BLINDAGEM DE TRANSPORTE ANTI-FALSO POSITIVO + EXPURGO DA PORTA 1234 + 17/17 PASSED NO PYTEST**

---

## 1. Auditoria Forense e Remediação Versão 1.1 (Homologação Argon & Opus 5.5)

1. **Expurgo da Rota Inativa da Porta 1234 (LM Studio):**
   - Removida a constante `URL_LM_STUDIO` e a função inoperante `chamar_lm_studio()` de [`router_tokens.py`](file:///d:/___SCRIPT/Router-Tokens/router_tokens.py);
   - Eliminados os atrasos síncronos de 62 segundos por recusa de conexão TCP (`WinError 10061`).

2. **Trava Mandatória de Transporte Anti-Falso Positivo:**
   - Adicionada lista determinística `PADROES_ERRO_INFRAESTRUTURA` (`[winerror `, `urlopen error`, `connection refused`, etc.);
   - O validador sintático [`validar_codigo_python()`](file:///d:/___SCRIPT/Router-Tokens/router_tokens.py) agora barra sumariamente mensagens de erro de socket, impedindo que exceções do sistema sejam classificadas como `APROVADO_TEXTO` em tarefas de texto livre (como normalização de endereço);
   - A invariante $\text{sucesso} \iff \text{transporte\_ok} \land \text{validação\_aprovada}$ foi formalmente restabelecida.

3. **Transporte Local com Resiliência (RTX 5090):**
   - Função [`chamar_ollama()`](file:///d:/___SCRIPT/Router-Tokens/router_tokens.py) atualizada com 2 tentativas e recuo progressivo de 250 ms na porta 11434, absorvendo contenções momentâneas de VRAM.

---

## 2. A Tríade Canônica de Benchmarks Homologados (Zero Regressão)

1. **Benchmark 1 — Pytest Expandido com Caça ao Bug ([`test_bateria_completa_router.py`](file:///d:/___SCRIPT/Router-Tokens/test_bateria_completa_router.py)):**
   - **Resultado:** **17/17 APROVADOS (100% PASSED em 57.20s)**;
   - Novo teste `test_17_bloqueio_falso_positivo_erro_infraestrutura_e_transporte` validando o disjuntor contra falsos positivos de transporte.

2. **Benchmark 2 — RouterEval Acadêmico MilkThink-Lab ([`benchmark_routereval_zamora.py`](file:///d:/___SCRIPT/Router-Tokens/benchmark_routereval_zamora.py)):**
   - **Resultado:** **16/16 APROVADOS (100% PASSED em 0.8s)**;
   - Índice de Retenção de Desempenho ($V_r$): **`1.0000`** (paridade perfeita com Oráculo);
   - Eficiência Econômica ($E_p$): **`72,5%` de economia** ponderada;
   - Over-Routing = **`0,0%`** | Under-Routing = **`0,0%`**;
   - Relatório: [`_entrega/router_eval_benchmark.json`](file:///d:/___SCRIPT/Router-Tokens/_entrega/router_eval_benchmark.json).

3. **Benchmark 3 — Promptfoo via LiteLLM Proxy Porta 4000 ([`promptfooconfig.yaml`](file:///d:/___SCRIPT/Router-Tokens/promptfooconfig.yaml)):**
   - **Resultado:** **10/10 APROVADOS (100% PASSED em 12 segundos)**;
   - Relatório: [`_entrega/promptfoo_resultado.json`](file:///d:/___SCRIPT/Router-Tokens/_entrega/promptfoo_resultado.json).

4. **Prova Real de Normalização de Endereço na RTX 5090:**
   - Tarefa: Normalização de endereço para o padrão dos Correios;
   - Desempenho: **441 ms** na RTX 5090 local a custo zero;
   - Auditoria: `sucesso: true` com corpo válido no padrão dos Correios registrado em [`_entrega/auditoria_roteamento.jsonl`](file:///d:/___SCRIPT/Router-Tokens/_entrega/auditoria_roteamento.jsonl).

---

## 3. Diretriz de Portabilidade e Governança

1. **Estação ZAMORA:** Unificada na porta 11434 com duplo operário local (`qwen2.5-coder:32b` e `deepseek-r1:32b`) + `qwen2.5-coder:7b`.
2. **Estação do Trabalho (16 GB):** [`litellm_config_trabalho_16gb.yaml`](file:///d:/___SCRIPT/Router-Tokens/litellm_config_trabalho_16gb.yaml) calibrado para `deepseek-r1:14b` e `qwen2.5-coder:7b`.
3. **Chancela Final:** Homologação conjunta emitida pelo Orquestrador Chefe Argon e pelo Auditor Chefe de Governança Opus 5.5 no Antigravity.
