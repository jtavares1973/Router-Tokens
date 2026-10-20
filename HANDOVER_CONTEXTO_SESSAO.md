# HANDOVER DE CONTEXTO DA SESSÃO — PROJETO `Router-Tokens`

**Última Atualização:** 20/10/2026 às 10:06 (Horário de Brasília)  
**Estação:** `ZAMORA` (AMD Ryzen 9 7950X | NVIDIA GeForce RTX 5090 32 GB GDDR7 | 64 GB RAM)  
**Status Global:** **HOMOLOGADO COM GRAU MÁXIMO (100% PASSED NO PROMPTFOO EM 12s + 16/16 PYTEST + LAUDO DE APROVAÇÃO DO OPUS 5.5 / ARGON)**

---

## 1. Benchmark Oficial com o Framework `promptfoo` ([`promptfooconfig.yaml`](file:///d:/___SCRIPT/Router-Tokens/promptfooconfig.yaml))

1. **Resultado Consolidado:**
   - **10 Testes Executados:** **10 APROVADOS (100% PASSED, 0 ERROS)**;
   - **Tempo Total da Suíte:** **12 segundos** (média de ~1,2s por teste na RTX 5090);
   - **Tokens Processados:** 1.757 tokens a **Custo Zero Real**;
   - **Relatório Oficial:** [`_entrega/promptfoo_resultado.json`](file:///d:/___SCRIPT/Router-Tokens/_entrega/promptfoo_resultado.json).

2. **As 3 Melhorias Homologadas pelo Opus 5.5 e Aplicadas:**
   - **Supressão Mandatória de Prosa:** O modelo entrega apenas o bloco de código tipado, reduzindo a saída de 350 tokens para ~55 tokens por resposta;
   - **Serialização de Concorrência na GPU (`maxConcurrency: 1`):** Permite que cada chamada usufrua de 100% da largura de banda dos Tensor Cores da RTX 5090 sem repartição de tensores na VRAM;
   - **Max Tokens Proporcional:** 512 para o modelo 7B e 1024 para o modelo 32B, evitando desperdício de tensores e impedindo truncamento acidental.

---

## 2. Topologia Operacional Homologada (Política 90/10 + LiteLLM Gateway)

1. **LiteLLM Proxy Universal (Porta `127.0.0.1:4000`):**
   - Configuração Canônica: [`litellm_config.yaml`](file:///d:/___SCRIPT/Router-Tokens/litellm_config.yaml)
   - Inicializador com Blindagem UTF-8: [`iniciar_litellm_proxy.py`](file:///d:/___SCRIPT/Router-Tokens/iniciar_litellm_proxy.py)
   - Modelos Declarados:
     * `zamora-executor-local` -> `ollama_chat/qwen2.5-coder:32b` (RTX 5090)
     * `zamora-executor-7b` -> `ollama_chat/qwen2.5-coder:7b` (RTX 5090)
     * `zamora-agentic-deepseek` -> `ollama_chat/deepseek-v4.1-flash:cloud` (Ollama Cloud)
     * `zamora-agentic-glm` -> `ollama_chat/glm-5.3:cloud` (Ollama Cloud)
     * `zamora-nuvem-flash` -> `gemini/gemini-2.5-flash`
     * `zamora-orquestrador-chefe` -> `gemini/gemini-2.5-pro` (Teto de 10%)

2. **Calibração de Memória VRAM na RTX 5090 (32 GB GDDR7):**
   - 31,6 GB residentes em VRAM dedicados para o Qwen 32B e 7B sem troca de modelos;
   - `OLLAMA_KV_CACHE_TYPE=q8_0` economizando 3,5 GB de atenção.

---

## 3. Resumo de Baterias de Testes Aprovadas
- **Promptfoo Benchmark:** 10/10 Testes Aprovados (`100% PASSED` em 12s);
- **Bateria Progressiva de 5 Níveis:** 100% Aprovada (do ultrassimples ao complexo);
- **Suíte Pytest + Hypothesis (16 Testes):** 16/16 Aprovados (`100% PASSED`);
- **Scrap Real Mercúrio OINA:** 3/3 Testes Aprovados com economia de 93,2% a 98,8% de tokens.
