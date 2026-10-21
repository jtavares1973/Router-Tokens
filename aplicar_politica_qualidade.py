# -*- coding: utf-8 -*-
"""Politica Qualidade Primeiro (v1.4) - aplicador idempotente e EOL-safe."""
import io

def load(p):
    with io.open(p, "r", encoding="latin-1", newline="") as f:
        s = f.read()
    eol = "\r\n" if "\r\n" in s else "\n"
    return s.replace("\r\n", "\n"), eol

def save(p, s, eol):
    if eol == "\r\n":
        s = s.replace("\n", "\r\n")
    with io.open(p, "w", encoding="latin-1", newline="") as f:
        f.write(s)

def sub1(code, old, new, name):
    if old not in code:
        raise SystemExit("ANCORA NAO ENCONTRADA (%s)" % name)
    if code.count(old) != 1:
        raise SystemExit("ANCORA MULTIPLA (%s): %d" % (name, code.count(old)))
    return code.replace(old, new, 1)

# ---------- 1. router_tokens.py ----------
p = "router_tokens.py"
code, eol = load(p)

if "POLITICA_QUALIDADE_PRIMEIRO" not in code:
    pol_blc = (
        "# ============================================================================\n"
        "# 0. POLITICA DE QUALIDADE PRIMEIRO (v1.4)\n"
        "# Objetivo prioritario: QUALIDADE, nao economia.\n"
        "#   - Topo da escada: Gemini 4.0 Argon (nivel Opus 5.5). Define criterio de\n"
        "#     aceite e revisa mudancas nao triviais.\n"
        "#   - Executores locais (Degrau 1) apenas para tarefas mecanicas de baixo\n"
        "#     risco (regex, renomeacao, docstring, lint, typo, log, traducao).\n"
        "#   - Escalonamento ocorre por falha de teste ou reprovacao na revisao,\n"
        "#     nunca por custo.\n"
        "#   - Setar POLITICA_QUALIDADE_PRIMEIRO = False restaura o modo legado\n"
        "#     90/10 para avaliacao comparativa (aprovado-na-primeira vs Opus).\n"
        "# ============================================================================\n"
        "POLITICA_QUALIDADE_PRIMEIRO: bool = True\n"
        "MODELO_TOPO_QUALIDADE: str = \"gemini-4-argon\"\n"
        "GATILHOS_MECANICOS: list = [\n"
        "    \"docstring\", \"comentari\", \"renome\", \"indentac\", \"pep8\", \"lint\",\n"
        "    \"typo\", \"traduzi\", \"converter encoding\", \"regex\", \"formatar\",\n"
        "    \"adicionar log\", \"print de debug\"\n"
        "]\n\n\n"
    )
    code = sub1(code, "class ResultadoDecisaoGEV", pol_blc + "class ResultadoDecisaoGEV", "politica-blc")

    old_default = (
        "    return (\n"
        "        \"DEGRAU_1_RTX5090_LOCAL\",\n"
        "        \"qwen2.5-coder:7b\",\n"
    )
    idx = code.rfind(old_default)
    if idx == -1:
        raise SystemExit("ANCORA NAO ENCONTRADA: default-classificador")
    end = code.find("\n    )", idx)
    if end == -1:
        raise SystemExit("FIM DO BLOCO NAO ENCONTRADO")
    end += len("\n    )")
    qual_new = (
        "    if POLITICA_QUALIDADE_PRIMEIRO:\n"
        "        eh_mecanica = any(g in texto_limpo for g in GATILHOS_MECANICOS)\n"
        "        if eh_mecanica:\n"
        "            return (\n"
        "                \"DEGRAU_1_RTX5090_LOCAL\",\n"
        "                \"qwen2.5-coder:7b\",\n"
        "                \"Politica Qualidade Primeiro: tarefa mecanica de baixo risco executada localmente a custo zero.\",\n"
        "            )\n"
        "        return (\n"
        "            \"DEGRAU_4_ARGON_ORQUESTRADOR\",\n"
        "            MODELO_TOPO_QUALIDADE,\n"
        "            \"Politica Qualidade Primeiro: tarefa nao mecanica delegada ao topo (Gemini 4.0 Argon / nivel Opus 5.5) para definir criterio de aceite e revisar.\",\n"
        "        )\n"
        "\n"
        "    # Modo legado 90/10 (avaliacao comparativa)\n"
        "    return (\n"
        "        \"DEGRAU_1_RTX5090_LOCAL\",\n"
        "        \"qwen2.5-coder:7b\",\n"
        "        \"Tarefa contida de arquivo unico/funcao/script: execucao local a custo zero na RTX 5090.\",\n"
        "    )"
    )
    code = code[:idx] + qual_new + code[end:]

    code = sub1(code,
        "        teste = payload.get(\"codigo_teste_assert\", None)\n"
        "        res = executar_roteamento(\n"
        "            instrucao=instr,\n"
        "            arquivos_envolvidos=arqs,\n"
        "            codigo_teste_assert=teste,\n"
        "        )",
        "        teste = payload.get(\"codigo_teste_assert\", None)\n"
        "        fc = payload.get(\"forcar_camada\", None)\n"
        "        res = executar_roteamento(\n"
        "            instrucao=instr,\n"
        "            arquivos_envolvidos=arqs,\n"
        "            codigo_teste_assert=teste,\n"
        "            forcar_camada=fc,\n"
        "        )",
        "lote-forcar")

    code = code.replace("versao_motor: str = \"1.3\"", "versao_motor: str = \"1.4\"")
    code = code.replace("versao_motor=\"1.3\",", "versao_motor=\"1.4\",")
    save(p, code, eol)
    print("router_tokens.py: politica aplicada")
else:
    print("router_tokens.py: ja aplicado, pulando")

# ---------- 2. test_bateria_completa_router.py ----------
p = "test_bateria_completa_router.py"
t, eol_t = load(p)
if "test_24_politica_qualidade_default_topo_argon" not in t:

    if "import router_tokens\n" not in t:
        t = sub1(t, "from router_tokens import (", "import router_tokens\n\nfrom router_tokens import (", "import-modulo")

    if "test09-forcamada" not in t and "forcar_camada=\"DEGRAU_1_RTX5090_LOCAL\"" not in t:
        t = sub1(t,
            "        codigo_teste_assert=\"assert limpar_matricula('Matr: 23.654-A') == '23654'\",",
            "        codigo_teste_assert=\"assert limpar_matricula('Matr: 23.654-A') == '23654'\",\n"
            "        forcar_camada=\"DEGRAU_1_RTX5090_LOCAL\",",
            "test09-forcar")

    t = sub1(t,
        "res_ok = executar_roteamento(\"Criar constante X = 1\", arquivos_envolvidos=1)",
        "res_ok = executar_roteamento(\"Criar constante X = 1\", arquivos_envolvidos=1, forcar_camada=\"DEGRAU_1_RTX5090_LOCAL\")",
        "test10-forcar")

    if t.count("simular_falha_local=True") != 1:
        raise SystemExit("ANCORA MULTIPLA/ausente: simular_falha_local=True (%d)" % t.count("simular_falha_local=True"))
    t = t.replace(
        "simular_falha_local=True)",
        "forcar_camada=\"DEGRAU_1_RTX5090_LOCAL\", simular_falha_local=True)",
        1,
    )

    t = sub1(t,
        "    lote = [\n"
        "        {\"instrucao\": \"Escreva def f1(): return 1\"},\n"
        "        {\"instrucao\": \"Escreva def f2(): return 2\"},\n"
        "        {\"instrucao\": \"Escreva def f3(): return 3\"},\n"
        "    ]",
        "    lote = [\n"
        "        {\"instrucao\": \"Escreva def f1(): return 1\", \"forcar_camada\": \"DEGRAU_1_RTX5090_LOCAL\"},\n"
        "        {\"instrucao\": \"Escreva def f2(): return 2\", \"forcar_camada\": \"DEGRAU_1_RTX5090_LOCAL\"},\n"
        "        {\"instrucao\": \"Escreva def f3(): return 3\", \"forcar_camada\": \"DEGRAU_1_RTX5090_LOCAL\"},\n"
        "    ]",
        "test22-forcar")

    t = sub1(t,
        "res = executar_roteamento(\"Escreva def somar(a, b): return a + b\")",
        "res = executar_roteamento(\"Escreva def somar(a, b): return a + b\", forcar_camada=\"DEGRAU_1_RTX5090_LOCAL\")",
        "test23-forcar")

    t = sub1(t, "assert r.versao_motor == \"1.3\"", "assert r.versao_motor == \"1.4\"", "test22-versao")

    start_marker = "    # Degrau 1: 1 arquivo simples"
    si = t.find(start_marker)
    if si == -1:
        raise SystemExit("ANCORA NAO ENCONTRADA: test07-start")
    ei_marker = "    assert m4 == \"gemini-4-argon\""
    ei = t.find(ei_marker, si)
    if ei == -1:
        raise SystemExit("ANCORA NAO ENCONTRADA: test07-end")
    ei += len(ei_marker)
    test07_new = (
        "    # Politica Qualidade Primeiro: tarefa mecanica de baixo risco -> Degrau 1 local\n"
        "    dm, mm, _ = classificar_tarefa_camada_a(\n"
        "        \"Renomear variaveis internas e ajustar indentacao do modulo\", arquivos_envolvidos=1\n"
        "    )\n"
        "    assert dm == \"DEGRAU_1_RTX5090_LOCAL\"\n"
        "    assert mm == \"qwen2.5-coder:7b\"\n"
        "\n"
        "    # Politica Qualidade Primeiro: tarefa nao mecanica -> topo Argon por padrao\n"
        "    dtopo, mtopo, motivo = classificar_tarefa_camada_a(\n"
        "        \"Criar funcao de formatacao de data\", arquivos_envolvidos=1\n"
        "    )\n"
        "    assert dtopo == \"DEGRAU_4_ARGON_ORQUESTRADOR\"\n"
        "    assert mtopo == \"gemini-4-argon\"\n"
        "    assert \"Qualidade Primeiro\" in motivo\n"
        "\n"
        "    # Degrau 2: 2 arquivos ou algoritmo complexo\n"
        "    d2, m2, _ = classificar_tarefa_camada_a(\"Realizar cruzamento relacional complexo\", arquivos_envolvidos=2)\n"
        "    assert d2 == \"DEGRAU_2_DEEPSEEK_763B\"\n"
        "\n"
        "    # Degrau 3: 3 ou 4 arquivos -> Escudo Gemini 3.8 Flash\n"
        "    d3, m3, _ = classificar_tarefa_camada_a(\"Ajustar modulos de servico\", arquivos_envolvidos=3)\n"
        "    assert d3 == \"DEGRAU_3_GEMINI_38_FLASH\"\n"
        "    assert m3 == \"gemini-3.8-flash\"\n"
        "\n"
        "    # Degrau 4: 5+ arquivos ou arquitetura global -> Orquestrador Argon\n"
        "    d4, m4, _ = classificar_tarefa_camada_a(\"Mudanca de arquitetura global do sistema\", arquivos_envolvidos=6)\n"
        "    assert d4 == \"DEGRAU_4_ARGON_ORQUESTRADOR\"\n"
        "    assert m4 == \"gemini-4-argon\""
    )
    t = t[:si] + test07_new + t[ei:]

    new_tests = (
        "\n\n"
        "# ============================================================================\n"
        "# 11. POLITICA QUALIDADE PRIMEIRO (v1.4)\n"
        "# ============================================================================\n"
        "def test_24_politica_qualidade_default_topo_argon():\n"
        "    \"\"\"v1.4: tarefa nao mecanica vai direto ao topo (Gemini 4.0 Argon).\"\"\"\n"
        "    camada, modelo, motivo = classificar_tarefa_camada_a(\n"
        "        \"Criar funcao que calcula juros compostos\", arquivos_envolvidos=1\n"
        "    )\n"
        "    assert camada == \"DEGRAU_4_ARGON_ORQUESTRADOR\"\n"
        "    assert modelo == \"gemini-4-argon\"\n"
        "    assert \"Qualidade Primeiro\" in motivo\n"
        "\n"
        "def test_25_politica_qualidade_mecanica_local():\n"
        "    \"\"\"v1.4: apenas tarefas mecanicas de baixo risco ficam no Degrau 1 local.\"\"\"\n"
        "    camada, modelo, _ = classificar_tarefa_camada_a(\n"
        "        \"Renomear variaveis e corrigir typo no docstring\", arquivos_envolvidos=1\n"
        "    )\n"
        "    assert camada == \"DEGRAU_1_RTX5090_LOCAL\"\n"
        "    assert modelo == \"qwen2.5-coder:7b\"\n"
        "\n"
        "def test_26_modo_legado_90_10_avaliacao_comparativa():\n"
        "    \"\"\"v1.4: desligar POLITICA_QUALIDADE_PRIMEIRO restaura o legado 90/10.\"\"\"\n"
        "    original = router_tokens.POLITICA_QUALIDADE_PRIMEIRO\n"
        "    try:\n"
        "        router_tokens.POLITICA_QUALIDADE_PRIMEIRO = False\n"
        "        camada, _, _ = classificar_tarefa_camada_a(\n"
        "            \"Criar funcao que calcula juros compostos\", arquivos_envolvidos=1\n"
        "        )\n"
        "        assert camada == \"DEGRAU_1_RTX5090_LOCAL\"\n"
        "    finally:\n"
        "        router_tokens.POLITICA_QUALIDADE_PRIMEIRO = original\n"
    )
    anchor = "if __name__ == \"__main__\":"
    if anchor not in t:
        raise SystemExit("ANCORA NAO ENCONTRADA: __main__")
    t = t.replace(anchor, new_tests + "\n\n" + anchor, 1)

    save(p, t, eol_t)
    print("test_bateria_completa_router.py: novos testes da politica aplicados")
else:
    print("test_bateria_completa_router.py: ja aplicado, pulando")

# ---------- 3. Configs LiteLLM ----------
changed_yaml = 0
for yf in ("litellm_config.yaml", "litellm_config_trabalho_16gb.yaml"):
    y, ey = load(yf)
    if "model: gemini/gemini-2.5-pro" in y:
        y = y.replace("model: gemini/gemini-2.5-pro", "model: gemini/gemini-4-argon")
        save(yf, y, ey)
        changed_yaml += 1
print("Yaml atualizados:", changed_yaml)

# ---------- 4. README ----------
txt = io.open("README.md", "r", encoding="utf-8").read()
if "POLITICA QUALIDADE PRIMEIRO" not in txt:
    with io.open("README.md", "a", encoding="utf-8", newline="") as f:
        f.write(
            "\n\n---\n\n"
            "# 3. POLITICA QUALIDADE PRIMEIRO (v1.4)\n\n"
            "Objetivo prioritario: **qualidade, nao economia**.\n\n"
            "- **Topo da escada: Gemini 4.0 Argon** (nivel Opus 5.5; alternativa: Opus 4.5 via Antigravity).\n"
            "- Argon **define o criterio de aceite** e **revisa mudancas nao triviais**.\n"
            "- Executores locais (RTX/Ollama) ficam **apenas para tarefas mecanicas de baixo risco**\n"
            "  (regex, renomeacao, docstring, lint, typo, log, traducao, conversao de encoding).\n"
            "- Escalonamento ocorre por **falha de teste ou reprovacao na revisao**, nunca por custo.\n"
            "- A validacao vai alem de `ast.parse`: assercoes funcionais sobre as tarefas reais\n"
            "  (`codigo_teste_assert` executado com timeout).\n"
            "- Metrica alvo: **aprovado-na-primeira e retrabalho**, comparados com Opus isolado\n"
            "  nas mesmas tarefas. Desligue `POLITICA_QUALIDADE_PRIMEIRO` para reproduzir o\n"
            "  modo legado 90/10 e rodar a comparacao.\n"
        )
    print("README.md: secao da politica adicionada")
else:
    print("README.md: ja aplicado, pulando")

print("PATCH OK")
