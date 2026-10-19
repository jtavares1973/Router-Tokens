# HANDOVER DE CONTEXTO DA SESSÃO — PROJETO `Router-Tokens`

**Última Atualização:** 19/10/2026 às 17:28 (Horário de Brasília)  
**Estação:** `ZAMORA` (AMD Ryzen 9 7950X | NVIDIA GeForce RTX 5090 32 GB GDDR7 | 64 GB RAM)  
**Status Global:** **HOMOLOGADO E OPERACIONAL (16/16 TESTES APROVADOS + LITELLM PROXY 4000 ATIVO COM RESIDÊNCIA DUPLA NA RTX 5090)**

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
     * `zamora-orquestrador-chefe` -> `gemini/gemini-2.5-pro` (Teto de 10%)

2. **Calibração de Memória VRAM na RTX 5090 (32 GB GDDR7):**
   - `OLLAMA_MAX_LOADED_MODELS=2`: Permite manter simultaneamente o Executor 32B (~19 GB) e o Fiscal 7B (~4.7 GB) residentes em VRAM.
   - `OLLAMA_KV_CACHE_TYPE=q8_0`: Compactação de 8 bits na memória temporária de atenção, economizando mais de 3,5 GB de VRAM em janelas de 32k.
   - `OLLAMA_KEEP_ALIVE=-1`: Impede descarga ociosa por timeout.
   - **Tempo de Inferência Medido (Qwen 32B Quente):** **`2.455 milissegundos`** para 150 tokens (> 60 tokens/segundo local a custo zero).

3. **Bypass Crítico do Fiscal GEV-Lite (`24 a 37 ms`):**
   - O fiscal binário determinístico (`qwen2.5-coder:7b`) conecta-se diretamente à porta nativa `http://localhost:11434/api/generate`, poupando de 15 a 30 ms de sobrecarga HTTP do proxy.

---

## 2. As 16 Suítes de Testes e Blindagem Anti-Piora de Código ([`test_bateria_completa_router.py`](file:///d:/___SCRIPT/Router-Tokens/test_bateria_completa_router.py))
- **`test_01` a `test_03` (Hypothesis Fuzzing — SGI):** 240 ataques caóticos garantindo integridade sintática (`100% PASSED`).
- **`test_04` a `test_06` (Furos de Borda):** Prosa técnica, múltiplos blocos markdown e bloqueio de `input()` interativo (`100% PASSED`).
- **`test_07` a `test_11` (Escada 4 Degraus, GEV-Lite em `24 ms`, Contratos e Auditoria):** Todos `PASSED`.
- **`test_12` a `test_16` (As 5 Travas Anti-Piora):**
  * Trava 1 (Anti-Mutilação / Preguiça de `# ... resto do código`) (`PASSED`);
  * Trava 2 (Anti-Exclusão de Funções existentes via AST) (`PASSED`);
  * Trava 3 (Anti-Comandos Destrutivos como `rmtree`, `remove`, `unlink`) (`PASSED`);
  * Trava 4 (Anti-Acentuação Corrompida / Mojibake) (`PASSED`);
  * Trava 5 (Disjuntor de 3s contra Loop Infinito em `while True`) (`PASSED`).

---

## 3. Laudo Pericial Homologado do Orquestrador de Cúpula (Opus / Argon)
- **Veredito:** Aprovado institucionalmente para produção sob a Política 90/10.
- **Ressalva Cumprida:** Resolução da dependência do SDK experimental MCP no ambiente Python local através de adaptação cirúrgica no `types.py` e `utils.py` do LiteLLM.
- **Pendência para o Próximo Turno:** Manter os serviços de suporte (Ollama e LiteLLM Proxy) ativos na inicialização da estação ZAMORA ou via tarefa automática do Windows.
