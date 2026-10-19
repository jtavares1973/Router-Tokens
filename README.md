# Router-Tokens — Orquestrador Inteligente 90/10 + Motor `GEV-Lite`

Motor de roteamento em **Escada de 4 Degraus** com **Fiscal Validador Anti-Piora (`24 ms`)**, projetado para economizar até **97,5% dos tokens** dos modelos de fronteira mantendo **100% de fidelidade e qualidade**.

---

## 1. Arquitetura da Escada de 4 Degraus

1. **Degrau 1 — Placa de Vídeo Local (Ollama `11434` / LM Studio `1234` — Custo Zero):**
   - Tenta resolver primeiro localmente (`qwen2.5-coder:7b`, `qwen3.8-32k:latest`, `qwen2.5-coder:32b`).
2. **Fiscal Validador Duplo (`0 a 27 ms` — Custo Zero):**
   - **Fiscal 1 (Exato):** Compilador Sintático Python (`ast.parse`) + Asserções Funcionais + **5 Travas Anti-Piora** (barra `# ... resto do código`, barra exclusão de funções existentes, bloqueia `rmtree`/`remove`/`input()`, detecta acento corrompido e corta loop infinito em 3s).
   - **Fiscal 2 (`GEV-Lite`):** Motor de Decisão de 1 Letra (`[A] APROVADO` / `[B] REPROVADO`) em **`24 a 37 ms`**.
3. **Degrau 2 — DeepSeek V4.1 (`763B` via Ollama Cloud — Custo Zero):**
   - Assume automaticamente no mesmo segundo se o Degrau 1 reprovar no Fiscal.
4. **Degrau 3 — Gemini 3.8 Flash (Escudo Rápido e Muito Barato):**
   - Assume tarefas de múltiplos arquivos moderados (3 a 4 arquivos) ou se o Degrau 2 falhar.
5. **Degrau 4 — Gemini 4 Argon (Orquestrador Chefe):**
   - Comanda a estratégia global e só entra na execução pesada se nem o 3.8 Flash resolver.

---

## 2. Como Usar no Computador do Trabalho

### Passo 1: Clonar o repositório
```powershell
git clone https://github.com/jtavares1973/Router-Tokens.git
cd Router-Tokens
pip install pytest hypothesis mcp
```

### Passo 2: Garantir o Ollama ou LM Studio rodando
- Se tiver **Ollama** instalado no trabalho: `ollama serve` (porta `11434`)
- Se tiver **LM Studio** instalado no trabalho: ligue o servidor local na porta `1234`
*(Mesmo em máquinas no trabalho com GPU menor ou CPU, o Degrau 2 `deepseek-v4.1-flash:cloud` via Ollama Cloud funciona a 100% de velocidade sem pesar na máquina local!)*

### Passo 3: Rodar a Bateria Completa de 16 Testes
```powershell
python test_bateria_completa_router.py
```
