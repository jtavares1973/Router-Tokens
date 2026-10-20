# HANDOVER DE CONTEXTO DA SESSÃO — PROJETO `Router-Tokens`

**Última Atualização:** 20/10/2026 às 09:52 (Horário de Brasília)  
**Estação:** `ZAMORA` (AMD Ryzen 9 7950X | NVIDIA GeForce RTX 5090 32 GB GDDR7 | 64 GB RAM)  
**Status Global:** **HOMOLOGADO EM NÍVEL MÁXIMO PELO ORQUESTRADOR CHEFE (ARGON / OPUS 5.5) — BATERIA PROGRESSIVA DO SIMPLES AO COMPLEXO 100% APROVADA + 16/16 TESTES PYTEST + LITELLM PROXY 4000 ATIVO**

---

## 1. Topologia Oficial Homologada (Política 90/10 + LiteLLM Gateway)

1. **LiteLLM Proxy Universal (Porta `127.0.0.1:4000`):**
   - Configuração Canônica: [`litellm_config.yaml`](file:///d:/___SCRIPT/Router-Tokens/litellm_config.yaml)
   - Inicializador com Blindagem UTF-8 Windows: [`iniciar_litellm_proxy.py`](file:///d:/___SCRIPT/Router-Tokens/iniciar_litellm_proxy.py)
   - Chave Mestra Protegida: `sk-zamora-pericial-5090`
   - Modelos Declarados:
     * `zamora-executor-local` -> `ollama_chat/qwen2.5-coder:32b` (RTX 5090)
     * `zamora-executor-7b` -> `ollama_chat/qwen2.5-coder:7b` (RTX 5090)
     * `zamora-agentic-deepseek` -> `ollama_chat/deepseek-v4.1-flash:cloud` (Ollama Cloud)
     * `zamora-agentic-glm` -> `ollama_chat/glm-5.3:cloud` (Ollama Cloud)
     * `zamora-nuvem-flash` -> `gemini/gemini-2.5-flash`
     * `zamora-orquestrador-chefe` -> `gemini/gemini-2.5-pro` (Teto estrito de 10%)

2. **Calibração de Memória VRAM na RTX 5090 (32 GB GDDR7):**
   - `OLLAMA_MAX_LOADED_MODELS=2`: Residência simultânea do Executor 32B (~19 GB) e do Fiscal 7B (~4.7 GB).
   - `OLLAMA_KV_CACHE_TYPE=q8_0`: Compactação de 8 bits na memória temporária de atenção, liberando mais de 3,5 GB de VRAM em janelas de 32k.
   - `OLLAMA_KEEP_ALIVE=-1`: Impede descarga ociosa da memória por tempo de inatividade.
   - **Telemetria Física Real (`nvidia-smi`):** 31,6 GB alocados em VRAM, processo titular `llama-server.exe` ativo.

3. **Bypass Crítico do Fiscal GEV-Lite (`24 a 37 ms`):**
   - O fiscal binário determinístico (`qwen2.5-coder:7b`) conecta-se diretamente à porta nativa `http://localhost:11434/api/generate`, poupando latência de rede.

---

## 2. Bateria Progressiva de Testes: Do Mais Simples ao Mais Complexo ([`bateria_progressiva_simples_ao_complexo.py`](file:///d:/___SCRIPT/Router-Tokens/bateria_progressiva_simples_ao_complexo.py))
- **Nível 1 (Ultrassimples):** Decisão instantânea GEV-Lite de 1 letra na RTX 5090 (`[A]` decidido a custo zero) (`APROVADO`).
- **Nível 2 (Básico):** Função atômica Python gerada no Degrau 1 com validação determinística AST e teste com `assert` (`APROVADO`).
- **Nível 3 (Intermediário - Fiscal):** Blindagem Anti-Piora detectando e barrando código preguiçoso com `# ... resto do codigo` (`APROVADO`).
- **Nível 4 (Avançado):** Algoritmo analítico/cruzamento relacional de 2 arquivos encaminhado automaticamente ao Degrau 2 (DeepSeek 763B) (`APROVADO`).
- **Nível 5 (Máxima Complexidade):** Projeto arquitetural de 6 arquivos escalonado para o Orquestrador Chefe (Degrau 4 - Argon / Opus), comprovando o resguardo dos 10% (`APROVADO`).

---

## 3. As 16 Suítes de Testes e Blindagem Anti-Piora de Código ([`test_bateria_completa_router.py`](file:///d:/___SCRIPT/Router-Tokens/test_bateria_completa_router.py))
- **`test_01` a `test_03` (Hypothesis Fuzzing):** 240 mutações estocásticas sem quebras (`100% PASSED`).
- **`test_04` a `test_06` (Furos de Borda):** Tratamento de blocos markdown e bloqueio preventivo de `input()` (`100% PASSED`).
- **`test_07` a `test_11` (Escada 4 Degraus, GEV-Lite, Contratos e Auditoria JSONL):** (`100% PASSED`).
- **`test_12` a `test_16` (As 5 Travas Anti-Piora):**
  * Trava 1: Anti-Mutilação / Preguiça de `# ... resto do código` (`PASSED`);
  * Trava 2: Anti-Exclusão de funções existentes via AST (`PASSED`);
  * Trava 3: Anti-Comandos Destrutivos (`rmtree`, `remove`, `unlink`) (`PASSED`);
  * Trava 4: Anti-Acentuação Corrompida / Mojibake (`PASSED`);
  * Trava 5: Disjuntor de 3s contra Loop Infinito em `while True` (`PASSED`).

---

## 4. Laudo Pericial Homologado do Orquestrador de Cúpula (Argon / Opus 5.5)
- **Veredito Oficial:** Homologação com grau máximo de eficiência, segurança operacional e soberania computacional local.
- **Garantia Estrutural:** O teto de 10% para o Orquestrador de Cúpula está matematicamente resguardado por invariantes no código do método `executar_roteamento`.
