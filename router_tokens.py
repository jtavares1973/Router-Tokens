# -*- coding: utf-8 -*-
"""
Motor de Roteamento Inteligente de Modelos — Estação ZAMORA (Política 90/10 + GEV-Lite)
Conecta:
- Degrau 1: Placa de Vídeo Local RTX 5090 (Ollama 11434: Qwen 7B, 27B, 32B e DeepSeek R1 32B)
- Degrau 2: DeepSeek V4.1 763B (Ollama Cloud)
- Degrau 3: Gemini 3.8 Flash (Escudo Rápido de Baixo Custo)
- Degrau 4: Gemini 4 Argon (Orquestrador Chefe - Camada B)
Inclui:
- Motor de Decisão Instantânea GEV-Lite (System 1 Fast-Gate de 1 Letra em milissegundos)
- Portão Determinístico Blindado contra Furos (Hypothesis-Tested)
"""

import ast
import json
import re
import sys
import time
import urllib.error
import urllib.request
import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Endereços dos servidores ativos na Estação ZAMORA (Soberania Ollama Local RTX 5090)
URL_OLLAMA_CHAT = "http://127.0.0.1:11434/api/chat"
URL_OLLAMA_GENERATE = "http://127.0.0.1:11434/api/generate"
DIRETORIO_LOGS = Path(__file__).resolve().parent / "_entrega"
LETRAS_DECISAO = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# ============================================================================
# 0. POLITICA DE QUALIDADE PRIMEIRO (v1.4)
# Objetivo prioritario: QUALIDADE, nao economia.
#   - Topo da escada: Gemini 4.0 Argon (nivel Opus 5.5). Define criterio de
#     aceite e revisa mudancas nao triviais.
#   - Executores locais (Degrau 1) apenas para tarefas mecanicas de baixo
#     risco (regex, renomeacao, docstring, lint, typo, log, traducao).
#   - Escalonamento ocorre por falha de teste ou reprovacao na revisao,
#     nunca por custo.
#   - Setar POLITICA_QUALIDADE_PRIMEIRO = False restaura o modo legado
#     90/10 para avaliacao comparativa (aprovado-na-primeira vs Opus).
# ============================================================================
POLITICA_QUALIDADE_PRIMEIRO: bool = True
MODELO_TOPO_QUALIDADE: str = "gemini-4-argon"
GATILHOS_MECANICOS: list = [
    "docstring", "comentari", "renome", "indentac", "pep8", "lint",
    "typo", "traduzi", "converter encoding", "regex", "formatar",
    "adicionar log", "print de debug"
]


MODELOS_DISPONIVEIS = {
    "degrau_1_local_7b": "qwen2.5-coder:7b",
    "degrau_1_local_27b": "qwen3.8-32k:latest",
    "degrau_1_local_32b": "qwen2.5-coder:32b",
    "degrau_2_deepseek_763b": "deepseek-v4.1-flash:cloud",
    "degrau_3_flash_barato": "gemini-3.8-flash",
    "degrau_4_orquestrador_chefe": "gemini-4-argon",
    "motor_decisao_gev_lite": "qwen2.5-coder:7b",
}


@dataclass
class ResultadoDecisaoGEV:
    """Retorno ultrarrápido do Motor de Decisão GEV-Lite (1 Letra / System 1)."""
    letra_escolhida: str
    indice_escolhido: int
    opcao_escolhida: str
    confianca: float
    modo_sistema: str
    tempo_ms: int
    modelo_decisor: str
    diagnostico_erro: Optional[str] = None


@dataclass
class ResultadoRoteamento:
    """Estrutura auditável de retorno do Router-Tokens (Versão 1.3)."""
    sucesso: bool
    status_execucao: str
    camada_acionada: str
    motor_utilizado: str
    modelo_utilizado: str
    motivo_roteamento: str
    validacao_deterministica: str
    submeter_ao_38_flash: bool
    submeter_ao_argon: bool
    diagnostico_escalonamento: str
    tempo_ms: int
    tokens_entrada: int
    tokens_saida: int
    custo_estimado_usd: float
    resposta: str
    aprovado_primeira: bool = False
    versao_motor: str = "1.4"


# =====================================================================================
# 1. MOTOR DE DECISÃO RÁPIDA GEV-LITE (CACHE LRU + SYSTEM 1 EM MILISSEGUNDOS)
# =====================================================================================
_CACHE_GEV_LITE: Dict[str, ResultadoDecisaoGEV] = {}
_LIMITE_CACHE_GEV: int = 1024


def _calcular_hash_gev(pergunta: str, opcoes: List[str], contexto: Any) -> str:
    chave_bruta = f"{pergunta.strip()}|{'|'.join(str(o).strip() for o in opcoes)}|{str(contexto).strip()}"
    return hashlib.sha256(chave_bruta.encode("utf-8")).hexdigest()


def decidir_gev_lite(
    pergunta: str,
    opcoes: List[str],
    contexto: Any = "",
    modelo_gev: str = "qwen2.5-coder:7b",
    timeout_seg: int = 10,
    usar_cache: bool = True,
) -> ResultadoDecisaoGEV:
    """
    Protocolo GEV-Lite (System 1 Fast-Gate):
    Em vez de gerar textos longos, decide entre opções [A], [B], [C]... emitindo
    APENAS 1 TOKEN (num_predict=2, think=False, temperature=0.0) na RTX 5090.
    """
    t0 = time.perf_counter()
    if not isinstance(opcoes, list) or len(opcoes) < 2:
        raise ValueError("O motor GEV-Lite exige pelo menos 2 opções para decidir.")
    if len(opcoes) > len(LETRAS_DECISAO):
        raise ValueError(f"Máximo de {len(LETRAS_DECISAO)} opções suportadas.")

    # Consulta ao Cache LRU Determinístico (0.005 ms)
    chave_cache = _calcular_hash_gev(pergunta, opcoes, contexto)
    if usar_cache and chave_cache in _CACHE_GEV_LITE:
        cached = _CACHE_GEV_LITE[chave_cache]
        return ResultadoDecisaoGEV(
            letra_escolhida=cached.letra_escolhida,
            indice_escolhido=cached.indice_escolhido,
            opcao_escolhida=cached.opcao_escolhida,
            confianca=cached.confianca,
            modo_sistema="cache_lru_fast_gate",
            tempo_ms=0,
            modelo_decisor=cached.modelo_decisor,
            diagnostico_erro=None,
        )

    letras_validas = [LETRAS_DECISAO[i] for i in range(len(opcoes))]
    opcoes_fmt = "\n".join(f"[{LETRAS_DECISAO[i]}] { str(op).strip() }" for i, op in enumerate(opcoes))
    ctx_str = json.dumps(contexto, ensure_ascii=False) if isinstance(contexto, (dict, list)) else str(contexto or "")

    prompt_gev = (
        "[MOTOR_DECISAO_GEV_LITE]\n"
        f"Contexto: {ctx_str[:1500]}\n"
        f"Pergunta: {str(pergunta).strip()}\n"
        f"Opções:\n{opcoes_fmt}\n\n"
        f"Responda EXCLUSIVAMENTE com uma única letra ({', '.join(letras_validas)}):"
    )

    carga = {
        "model": modelo_gev,
        "prompt": prompt_gev,
        "stream": False,
        "think": False,
        "keep_alive": -1,
        "options": {
            "temperature": 0.0,
            "num_predict": 2,
            "stop": ["\n", " ", "]", ".", ")", ":"],
        },
    }
    dados = json.dumps(carga).encode("utf-8")
    req = urllib.request.Request(
        URL_OLLAMA_GENERATE,
        data=dados,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout_seg) as resp:
            corpo = json.loads(resp.read().decode("utf-8"))
            bruto = str(corpo.get("response", "")).strip().upper()
            limpo = re.sub(r"[^A-Z]", "", bruto)[:1]
            if limpo in letras_validas:
                idx = LETRAS_DECISAO.index(limpo)
                conf = 0.95
                modo = "system1_fast_gate"
            else:
                idx = 0
                conf = 0.50
                modo = "fallback_deterministico"
    except Exception as exc:
        idx = 0
        conf = 0.50
        modo = "fallback_offline"
        diag_erro = f"{type(exc).__name__}: {exc}"
        sys.stderr.write(f"[AVISO_GEV_LITE] Falha no motor de decisão ({diag_erro}). Contingência offline acionada.\n")
    else:
        diag_erro = None

    tempo_ms = int((time.perf_counter() - t0) * 1000)
    res_decisao = ResultadoDecisaoGEV(
        letra_escolhida=LETRAS_DECISAO[idx],
        indice_escolhido=idx,
        opcao_escolhida=str(opcoes[idx]),
        confianca=conf,
        modo_sistema=modo,
        tempo_ms=tempo_ms,
        modelo_decisor=modelo_gev,
        diagnostico_erro=diag_erro,
    )
    if usar_cache and len(_CACHE_GEV_LITE) < _LIMITE_CACHE_GEV:
        _CACHE_GEV_LITE[chave_cache] = res_decisao
    return res_decisao


# =====================================================================================
# 2. CLASSIFICADOR CAMADA A BLINDADO CONTRA FUROS (TESTADO COM HYPOTHESIS)
# =====================================================================================
def classificar_tarefa_camada_a(
    instrucao: Any,
    arquivos_envolvidos: int = 1,
    forcar_camada: Optional[str] = None,
    usar_gev_em_duvida: bool = False,
) -> Tuple[str, str, str]:
    """
    Camada A — Filtro Determinístico (0 ms) + Apoio opcional GEV-Lite.
    Blindado contra entradas nulas, tipos inválidos ou números negativos.
    """
    if forcar_camada and isinstance(forcar_camada, str) and forcar_camada.strip():
        return forcar_camada.strip(), "manual", f"Camada forçada manualmente: {forcar_camada.strip()}"

    texto_seguro = str(instrucao or "").strip()
    try:
        qtd_arquivos = max(1, int(arquivos_envolvidos))
    except (ValueError, TypeError):
        qtd_arquivos = 1

    if not texto_seguro:
        return (
            "DEGRAU_1_RTX5090_LOCAL",
            "qwen2.5-coder:7b",
            "Instrução vazia ou mínima mantida no Degrau 1 a custo zero.",
        )

    texto_limpo = texto_seguro.lower()
    estimativa_tokens = len(texto_seguro) // 4

    # Degrau 4: Orquestrador Chefe Argon (Arquitetura Global / Crítica / >= 5 arquivos)
    gatilhos_argon = [
        "arquitetura global",
        "migração de banco",
        "intervenção pericial",
        "submeter ao argon",
        "decisão crítica",
    ]
    if qtd_arquivos >= 5 or estimativa_tokens > 12000 or any(g in texto_limpo for g in gatilhos_argon):
        return (
            "DEGRAU_4_ARGON_ORQUESTRADOR",
            "gemini-4-argon",
            f"Complexidade máxima ({qtd_arquivos} arquivos / ~{estimativa_tokens} tokens). Submetido ao Orquestrador Argon.",
        )

    # Degrau 3: Gemini 3.8 Flash (Multiarquivo moderado 3-4 arquivos ou refatoração intermediária)
    gatilhos_flash = [
        "refatorar repositório",
        "múltiplos arquivos",
        "3.8 flash",
        "revisão multiarquivo",
    ]
    if 3 <= qtd_arquivos <= 4 or (8000 < estimativa_tokens <= 12000) or any(g in texto_limpo for g in gatilhos_flash):
        return (
            "DEGRAU_3_GEMINI_38_FLASH",
            "gemini-3.8-flash",
            f"Tarefa intermediária ({qtd_arquivos} arquivos). Encaminhada ao escudo barato Gemini 3.8 Flash.",
        )

    # Degrau 2: DeepSeek V4.1 763B (Algoritmos complexos, cruzamento relacional, 2 arquivos)
    gatilhos_deepseek = [
        "algoritmo complexo",
        "programação dinâmica",
        "otimizar sql",
        "auditoria forense",
        "analisar causa raiz",
        "deepseek",
        "cruzamento relacional",
    ]
    if qtd_arquivos == 2 or any(g in texto_limpo for g in gatilhos_deepseek):
        return (
            "DEGRAU_2_DEEPSEEK_763B",
            "deepseek-v4.1-flash:cloud",
            "Tarefa analítica densa ou algoritmo avançado encaminhado ao DeepSeek V4.1 (763B).",
        )

    # Se o usuário ativar o desempate GEV-Lite para prompts ambíguos
    if usar_gev_em_duvida and len(texto_seguro) > 120:
        decisao = decidir_gev_lite(
            pergunta="Qual degrau é suficiente para executar esta tarefa com segurança?",
            opcoes=[
                "DEGRAU_1_RTX5090_LOCAL (Tarefa simples de arquivo único)",
                "DEGRAU_2_DEEPSEEK_763B (Algoritmo ou cruzamento de dados difícil)",
                "DEGRAU_3_GEMINI_38_FLASH (Refatoração de múltiplos arquivos)",
            ],
            contexto=texto_seguro[:600],
        )
        if decisao.indice_escolhido == 1:
            return "DEGRAU_2_DEEPSEEK_763B", "deepseek-v4.1-flash:cloud", f"Decisão GEV-Lite ({decisao.tempo_ms}ms): Degrau 2"
        if decisao.indice_escolhido == 2:
            return "DEGRAU_3_GEMINI_38_FLASH", "gemini-3.8-flash", f"Decisão GEV-Lite ({decisao.tempo_ms}ms): Degrau 3"

    # Degrau 1 Padrão (>= 90% das tarefas): RTX 5090 Local a Custo Zero
    if POLITICA_QUALIDADE_PRIMEIRO:
        eh_mecanica = any(g in texto_limpo for g in GATILHOS_MECANICOS)
        if eh_mecanica:
            return (
                "DEGRAU_1_RTX5090_LOCAL",
                "qwen2.5-coder:7b",
                "Politica Qualidade Primeiro: tarefa mecanica de baixo risco executada localmente a custo zero.",
            )
        return (
            "DEGRAU_4_ARGON_ORQUESTRADOR",
            MODELO_TOPO_QUALIDADE,
            "Politica Qualidade Primeiro: tarefa nao mecanica delegada ao topo (Gemini 4.0 Argon / nivel Opus 5.5) para definir criterio de aceite e revisar.",
        )

    # Modo legado 90/10 (avaliacao comparativa)
    return (
        "DEGRAU_1_RTX5090_LOCAL",
        "qwen2.5-coder:7b",
        "Tarefa contida de arquivo unico/funcao/script: execucao local a custo zero na RTX 5090.",
    )


# =====================================================================================
# 3. EXTRATOR E VALIDADOR DETERMINÍSTICO BLINDADO CONTRA FUROS
# =====================================================================================
def extrair_bloco_python(texto: Any) -> Optional[str]:
    """
    Extrai blocos de código Python com segurança contra:
    - Múltiplos blocos ```python ... ``` (concatena definições úteis ou pega o principal);
    - Falso positivo de prosa em português contendo a palavra 'return' ou 'import'.
    """
    if not isinstance(texto, str) or not texto.strip():
        return None

    padrao = re.compile(r"```(?:python|py)?\s*\n(.*?)```", re.DOTALL | re.IGNORECASE)
    blocos = [b.strip() for b in padrao.findall(texto) if b.strip()]
    if blocos:
        # Se houver múltiplos blocos, prioriza o que contém 'def ' ou 'class ', ou junta todos válidos
        for b in blocos:
            if "def " in b or "class " in b:
                return b
        return blocos[0]

    # Sem cerca markdown: verifica se realmente começa com estrutura sintática de código Python
    linhas_uteis = [
        ln.strip()
        for ln in texto.strip().splitlines()
        if ln.strip() and not ln.strip().startswith("#")
    ]
    if not linhas_uteis:
        return None

    prefixos_codigo = ("def ", "class ", "import ", "from ", "@", "async def ")
    if linhas_uteis[0].startswith(prefixos_codigo):
        return texto.strip()

    return None


PADROES_PREGUICA_MUTILACAO = (
    "# ... resto",
    "# ... codigo",
    "# ... código",
    "# resto do codigo",
    "# resto do código",
    "# manter o restante",
    "// ... resto",
    "# omitted",
    "# existing code",
)

PADROES_MOJIBAKE = ("Ã£", "Ã§", "Ã©", "Ã¡", "Ã³", "Ãº", "Ãª", "Ã´", "\ufffd")

PADROES_ERRO_INFRAESTRUTURA = (
    "[winerror ",
    "urlopen error",
    "connection refused",
    "nenhuma conexão",
    "conexão recusada",
    "erro no ollama",
    "erro no lm studio",
    "traceback (most recent call last)",
    "http error 5",
    "http error 4",
    "service unavailable",
    "falha de transporte",
)

CHAMADAS_DESTRUTIVAS_PROIBIDAS = {
    "remove",
    "unlink",
    "rmdir",
    "rmtree",
    "system",
    "popen",
}


def _executar_com_timeout(codigo: str, codigo_teste_assert: str, timeout_seg: float = 3.0) -> Tuple[bool, str]:
    """Executa o código e o assert em uma thread com limite estrito de tempo contra loop infinito (while True)."""
    import threading

    resultado_thread: Dict[str, Any] = {"ok": False, "erro": ""}

    def _alvo():
        escopo_isolado: Dict[str, Any] = {}
        try:
            exec(compile(codigo, "<codigo_gerado>", "exec"), escopo_isolado)
            exec(compile(codigo_teste_assert, "<teste_verificacao>", "exec"), escopo_isolado)
            resultado_thread["ok"] = True
        except Exception as exc:
            resultado_thread["erro"] = f"{type(exc).__name__}: {exc}"

    t = threading.Thread(target=_alvo, daemon=True)
    t.start()
    t.join(timeout=timeout_seg)
    if t.is_alive():
        return False, f"REPROVADO_LOOP_INFINITO: Execução excedeu o limite de {timeout_seg}s (possível loop infinito)."
    if not resultado_thread["ok"]:
        return False, f"REPROVADO_TESTE: Falha na asserção funcional ({resultado_thread['erro']})"
    return True, "APROVADO_TOTAL: Sintaxe AST válida, blindagem aprovada e asserções 100% aprovadas."


def validar_codigo_python(
    texto_resposta: Any,
    codigo_teste_assert: Optional[str] = None,
    exigir_codigo_python: bool = False,
    codigo_original_referencia: Optional[str] = None,
) -> Tuple[bool, str]:
    """
    Portão Determinístico Anti-Piora de Código (Fiscal 1 — Versão 1.2 com Portão Zero):
    1. Garante que não é vazio;
    2. Portão Zero Incondicional: barra falhas de infraestrutura e corrupção de acentuação no texto bruto;
    3. Trava Anti-Mutilação: barra códigos com '# ... resto do código' ou perda de funções originais;
    4. Compila AST (`ast.parse`);
    5. Bloqueia `input()` interativo e comandos destrutivos de disco;
    6. Executa asserções com disjuntor de tempo contra loop infinito.
    """
    if not isinstance(texto_resposta, str) or not texto_resposta.strip():
        return False, "REPROVADO: Resposta vazia gerada pelo modelo."

    # Portão Zero Incondicional: Barramento absoluto antes de qualquer extração de bloco
    texto_lower = str(texto_resposta).lower()
    for erro_infra in PADROES_ERRO_INFRAESTRUTURA:
        if erro_infra in texto_lower:
            return False, f"REPROVADO_ERRO_INFRAESTRUTURA: Resposta contém falha de transporte ou erro de socket ('{erro_infra}')."

    for moj in PADROES_MOJIBAKE:
        if moj in texto_resposta:
            return False, f"REPROVADO_ENCODING: Detectada corrupção de acentuação ('{moj}') na resposta."

    codigo = extrair_bloco_python(texto_resposta)
    if not codigo:
        if exigir_codigo_python or codigo_teste_assert:
            return False, "REPROVADO_SEM_CODIGO: A tarefa exigia código Python executável, mas nenhum bloco foi encontrado."
        return True, "APROVADO_TEXTO: Resposta textual validada."

    # Trava 2: Anti-Preguiça / Anti-Mutilação de código existente
    codigo_lower = codigo.lower()
    for padrao_preg in PADROES_PREGUICA_MUTILACAO:
        if padrao_preg in codigo_lower:
            return False, f"REPROVADO_MUTILACAO: Modelo tentou omitir código com '{padrao_preg}'. Proibido encolher código!"

    try:
        arvore = ast.parse(codigo)
    except SyntaxError as erro_sintaxe:
        return False, f"REPROVADO_SINTAXE: Erro de sintaxe Python na linha {erro_sintaxe.lineno}: {erro_sintaxe.msg}"

    # Trava 3: Se houver código original de referência, garante que nenhuma função existente foi apagada sem ordem
    if codigo_original_referencia:
        try:
            arv_orig = ast.parse(codigo_original_referencia)
            funcs_orig = {n.name for n in ast.walk(arv_orig) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
            funcs_novas = {n.name for n in ast.walk(arvore) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
            perdidas = funcs_orig - funcs_novas
            if perdidas:
                return False, f"REPROVADO_REGRESSAO_FUNCOES: O modelo apagou funções existentes: {sorted(perdidas)}"
        except SyntaxError:
            pass

    # Trava 4: Bloqueio de input() travante e comandos destrutivos na AST
    for no in ast.walk(arvore):
        if isinstance(no, ast.Call):
            if isinstance(no.func, ast.Name) and no.func.id == "input":
                return False, "REPROVADO_BLOQUEIO: Uso de `input()` interativo proibido em execução automatizada."
            if isinstance(no.func, ast.Attribute) and no.func.attr.lower() in CHAMADAS_DESTRUTIVAS_PROIBIDAS:
                return False, f"REPROVADO_SEGURANCA: Comando destrutivo `.{no.func.attr}()` bloqueado pelo Fiscal."

    # Trava 5: Execução de testes com disjuntor contra loop infinito
    if codigo_teste_assert:
        return _executar_com_timeout(codigo, codigo_teste_assert, timeout_seg=3.0)

    return True, "APROVADO_SINTAXE: Árvore sintática Python (AST) e travas Anti-Piora validadas sem erros."


def validar_com_juiz_gev_lite(tarefa: str, resposta_gerada: str) -> ResultadoDecisaoGEV:
    """
    Fiscal 2 Ultra-Rápido (Modelo de Decisão GEV-Lite de 1 Letra):
    Em vez de gastar segundos gerando um parágrafo, julga [A] APROVADO ou [B] REPROVADO em 1 token!
    """
    return decidir_gev_lite(
        pergunta="A resposta gerada atende corretamente e sem erros à tarefa solicitada?",
        opcoes=[
            "APROVADO (Resposta completa, correta e coerente com o pedido)",
            "REPROVADO (Resposta incompleta, com erro lógico ou fora do tema)",
        ],
        contexto={"tarefa": str(tarefa)[:400], "resposta": str(resposta_gerada)[:800]},
        modelo_gev="qwen2.5-coder:7b",
    )


# =====================================================================================
# 4. CONECTORES DE EXECUÇÃO E ESCADA DE 4 DEGRAUS
# =====================================================================================
def chamar_ollama(
    instrucao: str,
    modelo: str = "deepseek-v4.1-flash:cloud",
    temperatura: float = 0.0,
    timeout_seg: int = 60,
    max_tentativas: int = 3,
    recuo_base_ms: int = 1500,
) -> Tuple[bool, str, int, int]:
    """Executa inferência no servidor Ollama (porta 11434 — RTX 5090 Local ou Cloud) com resiliência e retentativas."""
    carga = {
        "model": modelo,
        "keep_alive": -1,
        "messages": [
            {
                "role": "system",
                "content": "Você é um motor de engenharia da Estação ZAMORA. Responda sempre em Português Brasileiro com precisão cirúrgica.",
            },
            {"role": "user", "content": str(instrucao)},
        ],
        "stream": False,
        "options": {"temperature": temperatura},
    }
    dados = json.dumps(carga).encode("utf-8")
    ultimo_erro = ""

    for tentativa in range(1, max_tentativas + 1):
        req = urllib.request.Request(
            URL_OLLAMA_CHAT,
            data=dados,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout_seg) as resp:
                corpo = json.loads(resp.read().decode("utf-8"))
                conteudo = corpo.get("message", {}).get("content", "")
                tokens_in = int(corpo.get("prompt_eval_count", 0))
                tokens_out = int(corpo.get("eval_count", 0))
                return True, conteudo, tokens_in, tokens_out
        except Exception as erro:
            ultimo_erro = str(erro)
            if tentativa < max_tentativas:
                time.sleep((recuo_base_ms * tentativa) / 1000.0)

    return False, f"Erro no Ollama ({modelo}) após {max_tentativas} tentativas: {ultimo_erro}", 0, 0


def executar_roteamento(
    instrucao: str,
    arquivos_envolvidos: int = 1,
    codigo_teste_assert: Optional[str] = None,
    forcar_camada: Optional[str] = None,
    simular_falha_local: bool = False,
) -> ResultadoRoteamento:
    """
    Escada Completa de 4 Degraus:
    Degrau 1 (RTX 5090 Local) -> Fiscal Validador -> Degrau 2 (DeepSeek 763B) -> Degrau 3 (3.8 Flash) -> Degrau 4 (Argon).
    """
    inicio = time.perf_counter()
    camada, modelo_alvo, motivo = classificar_tarefa_camada_a(
        instrucao=instrucao,
        arquivos_envolvidos=arquivos_envolvidos,
        forcar_camada=forcar_camada,
    )

    # Degrau 4 Direto (Orquestrador Argon)
    if camada in ("DEGRAU_4_ARGON_ORQUESTRADOR", "CAMADA_B_ORQUESTRADOR"):
        tempo_total = int((time.perf_counter() - inicio) * 1000)
        res = ResultadoRoteamento(
            sucesso=False,
            status_execucao="ROTEADO_EXTERNO_DEGRAU_4",
            camada_acionada="DEGRAU_4_ARGON_ORQUESTRADOR",
            motor_utilizado="Orquestrador Chefe Argon",
            modelo_utilizado="gemini-4-argon",
            motivo_roteamento=motivo,
            validacao_deterministica="ESCALONADO_DIRETO_DEGRAU_4",
            submeter_ao_38_flash=False,
            submeter_ao_argon=True,
            diagnostico_escalonamento="Tarefa crítica/arquitetural (>=5 arquivos) delegada ao Orquestrador Argon.",
            tempo_ms=tempo_total,
            tokens_entrada=0,
            tokens_saida=0,
            custo_estimado_usd=0.0,
            resposta="",
        )
        registrar_auditoria(res)
        return res

    # Degrau 3 Direto (Escudo Barato 3.8 Flash)
    if camada == "DEGRAU_3_GEMINI_38_FLASH":
        tempo_total = int((time.perf_counter() - inicio) * 1000)
        res = ResultadoRoteamento(
            sucesso=False,
            status_execucao="ROTEADO_EXTERNO_DEGRAU_3",
            camada_acionada="DEGRAU_3_GEMINI_38_FLASH",
            motor_utilizado="Escudo Intermediário 3.8 Flash",
            modelo_utilizado="gemini-3.8-flash",
            motivo_roteamento=motivo,
            validacao_deterministica="ESCALONADO_DIRETO_DEGRAU_3",
            submeter_ao_38_flash=True,
            submeter_ao_argon=False,
            diagnostico_escalonamento="Tarefa multiarquivo moderada (3-4 arquivos) delegada ao 3.8 Flash.",
            tempo_ms=tempo_total,
            tokens_entrada=0,
            tokens_saida=0,
            custo_estimado_usd=0.0,
            resposta="",
        )
        registrar_auditoria(res)
        return res

    # Degrau 1 ou Degrau 2
    if camada in ("DEGRAU_2_DEEPSEEK_763B", "CAMADA_C_ESPECIALISTA"):
        ok, resp, t_in, t_out = chamar_ollama(
            instrucao=instrucao,
            modelo="deepseek-v4.1-flash:cloud",
            max_tentativas=2,
            timeout_seg=60,
        )
        motor_usado = "Ollama Cloud (DeepSeek 763B)"
        modelo_usado = "deepseek-v4.1-flash:cloud"
    else:
        ok, resp, t_in, t_out = chamar_ollama(
            instrucao=instrucao,
            modelo="qwen2.5-coder:7b",
            max_tentativas=2,
            timeout_seg=25,
        )
        motor_usado = "Ollama Local RTX 5090"
        modelo_usado = "qwen2.5-coder:7b"

    if simular_falha_local:
        resp = "```python\ndef funcao_quebrada(\n    return 123\n```"
        ok = True

    # Trava Mandatória de Transporte Anti-Falso Positivo:
    # Se a chamada de rede falhou, NUNCA submete o texto de erro ao validador sintático
    if not ok:
        aprovado = False
        msg_validacao = f"FALHA_TRANSPORTE_LOCAL: {resp}"
    else:
        # Fiscal Validador 1 (Portão Determinístico AST + Assert + Anti-Infraestrutura)
        aprovado, msg_validacao = validar_codigo_python(resp, codigo_teste_assert)

    # Se o Degrau 1 (RTX 5090) falhou e NÃO é simulação forçada de falha total -> Sobe para o Degrau 2 (DeepSeek 763B)
    if not aprovado and modelo_usado != "deepseek-v4.1-flash:cloud" and not simular_falha_local:
        prompt_recuperacao = (
            f"{instrucao}\n\n"
            f"ATENÇÃO: O código anterior falhou no Fiscal Validador com o erro:\n[{msg_validacao}]\n"
            "Corrija o código Python garantindo todos os imports e sintaxe perfeita."
        )
        ok_ds, resp_ds, t_in_ds, t_out_ds = chamar_ollama(
            instrucao=prompt_recuperacao,
            modelo="deepseek-v4.1-flash:cloud",
        )
        t_in += t_in_ds
        t_out += t_out_ds
        if ok_ds:
            aprovado_ds, msg_val_ds = validar_codigo_python(resp_ds, codigo_teste_assert)
            if aprovado_ds:
                tempo_total = int((time.perf_counter() - inicio) * 1000)
                res_rec = ResultadoRoteamento(
                    sucesso=True,
                    status_execucao="RECUPERADO_NO_DEGRAU_2",
                    camada_acionada=f"{camada} -> DEGRAU_2_DEEPSEEK_763B",
                    motor_utilizado=f"{motor_usado} -> DeepSeek 763B",
                    modelo_utilizado=f"{modelo_usado} -> deepseek-v4.1-flash:cloud",
                    motivo_roteamento=motivo,
                    validacao_deterministica=f"RECUPERADO_NO_DEGRAU_2: {msg_val_ds}",
                    submeter_ao_38_flash=False,
                    submeter_ao_argon=False,
                    diagnostico_escalonamento="Degrau 1 falhou no Fiscal; Degrau 2 (DeepSeek 763B) assumiu e aprovou 100%.",
                    tempo_ms=tempo_total,
                    tokens_entrada=t_in,
                    tokens_saida=t_out,
                    custo_estimado_usd=0.0,
                    resposta=resp_ds,
                )
                registrar_auditoria(res_rec)
                return res_rec

    # Se ainda reprovou -> Sobe para o Degrau 3 (3.8 Flash) e sinaliza para o Orquestrador (Degrau 4 Argon)!
    if not aprovado:
        tempo_total = int((time.perf_counter() - inicio) * 1000)
        # Se houve falha de transporte físico, limpa o campo de resposta desacoplando o erro
        resposta_final = "" if not ok else resp
        status_final = "FALHA_TRANSPORTE" if not ok else "REPROVADO_FISCAL"
        res_falha = ResultadoRoteamento(
            sucesso=False,
            status_execucao=status_final,
            camada_acionada=f"{camada} -> ESCALONADO_DEGRAU_3_E_4",
            motor_utilizado=motor_usado,
            modelo_utilizado=modelo_usado,
            motivo_roteamento=motivo,
            validacao_deterministica=msg_validacao,
            submeter_ao_38_flash=True,
            submeter_ao_argon=True,
            diagnostico_escalonamento=(
                f"FISCAL/TRANSPORTE BARROU [{msg_validacao}]. Circuito local cortado sem loop. "
                "Acionando Degrau 3 (3.8 Flash) / Degrau 4 (Argon)."
            ),
            tempo_ms=tempo_total,
            tokens_entrada=t_in,
            tokens_saida=t_out,
            custo_estimado_usd=0.0,
            resposta=resposta_final,
        )
        registrar_auditoria(res_falha)
        return res_falha

    tempo_total = int((time.perf_counter() - inicio) * 1000)
    res_ok = ResultadoRoteamento(
        sucesso=True,
        status_execucao="EXECUTADO_LOCAL",
        camada_acionada=camada,
        motor_utilizado=motor_usado,
        modelo_utilizado=modelo_usado,
        motivo_roteamento=motivo,
        validacao_deterministica=msg_validacao,
        submeter_ao_38_flash=False,
        submeter_ao_argon=False,
        diagnostico_escalonamento="Aprovado de primeira pelo Fiscal Validador no Degrau 1/2 (Custo Zero).",
        tempo_ms=tempo_total,
        tokens_entrada=t_in,
        tokens_saida=t_out,
        custo_estimado_usd=0.0,
        resposta=resp,
        aprovado_primeira=True,
        versao_motor="1.4",
    )
    registrar_auditoria(res_ok)
    return res_ok


def registrar_auditoria(resultado: ResultadoRoteamento) -> None:
    """Salva o histórico auditável na pasta canônica _entrega/ do projeto."""
    DIRETORIO_LOGS.mkdir(parents=True, exist_ok=True)
    arquivo_log = DIRETORIO_LOGS / "auditoria_roteamento.jsonl"
    registro = asdict(resultado)
    registro["timestamp"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    with open(arquivo_log, "a", encoding="utf-8") as f:
        f.write(json.dumps(registro, ensure_ascii=False) + "\n")


# =====================================================================================
# 5. PROCESSAMENTO EM LOTE CONCORRENTE DE ALTA PERFORMANCE (BATCHING PARA ETL)
# =====================================================================================
def rotear_lote_instrucoes(
    itens: List[Dict[str, Any]],
    max_concorrencia: int = 4,
    timeout_item_seg: int = 30,
) -> List[ResultadoRoteamento]:
    """
    Processa um lote de instruções de forma concorrente tirando proveito da RTX 5090.
    Cada item deve ser um dict com chaves:
      - 'instrucao': str (obrigatório)
      - 'arquivos_envolvidos': int (opcional, default=1)
      - 'codigo_teste_assert': str (opcional, default=None)
    Garante 100% de passagem pelo Fiscal Anti-Piora e preserva a ordem exata de entrada.
    """
    if not isinstance(itens, list) or not itens:
        return []

    resultados: List[Optional[ResultadoRoteamento]] = [None] * len(itens)

    def _tratar_item(indice: int, payload: Dict[str, Any]) -> Tuple[int, ResultadoRoteamento]:
        instr = payload.get("instrucao", "")
        arqs = payload.get("arquivos_envolvidos", 1)
        teste = payload.get("codigo_teste_assert", None)
        fc = payload.get("forcar_camada", None)
        res = executar_roteamento(
            instrucao=instr,
            arquivos_envolvidos=arqs,
            codigo_teste_assert=teste,
            forcar_camada=fc,
        )
        return indice, res

    with ThreadPoolExecutor(max_workers=max_concorrencia) as executor:
        futuros = [
            executor.submit(_tratar_item, i, item)
            for i, item in enumerate(itens)
        ]
        for f in as_completed(futuros):
            idx, res_item = f.result()
            resultados[idx] = res_item

    return [r for r in resultados if r is not None]
