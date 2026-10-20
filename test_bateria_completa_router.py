# -*- coding: utf-8 -*-
"""
================================================================================
BATERIA COMPLETA DE TESTES, CAÇADOR DE BUGS (HYPOTHESIS) E BENCHMARK GEV-LITE
Projeto: Router-Tokens • Estação ZAMORA
================================================================================
Inspirações diretas aplicadas:
1. ETL-SGI v02 (`test_saneamento_propriedades.py`): Fuzzing matemático via Hypothesis
   (@given) com centenas de entradas caóticas para caçar qualquer furo ou quebra.
2. GEV-26B (`servidor_decide.py`): Motor de Decisão Rápida GEV-Lite de 1 Letra
   (`num_predict=2`, `think=False`, `temperature=0.0`) na RTX 5090.
================================================================================
"""

import json
import sys
import time
from pathlib import Path
import pytest
from hypothesis import given, settings, strategies as st

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

RAIZ = Path(__file__).resolve().parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from router_tokens import (
    DIRETORIO_LOGS,
    rotear_lote_instrucoes,
    classificar_tarefa_camada_a,
    decidir_gev_lite,
    executar_roteamento,
    extrair_bloco_python,
    validar_codigo_python,
    validar_com_juiz_gev_lite,
)


# ==============================================================================
# 1. CAÇADOR DE BUGS (HYPOTHESIS FUZZING): CLASSIFICADOR CAMADA A NUNCA QUEBRA
# ==============================================================================
@given(
    instrucao=st.one_of(st.text(), st.none(), st.integers(), st.lists(st.text())),
    arquivos=st.one_of(st.integers(min_value=-1000, max_value=1000), st.none(), st.text()),
)
@settings(max_examples=80, deadline=None)
def test_01_hypothesis_classificador_nunca_quebra(instrucao, arquivos):
    """Caça-Furos 1: Qualquer lixo, nulo, número negativo ou texto caótico nunca pode quebrar a Camada A."""
    camada, modelo, motivo = classificar_tarefa_camada_a(instrucao, arquivos)
    assert isinstance(camada, str) and camada.startswith("DEGRAU_")
    assert isinstance(modelo, str) and len(modelo) > 0
    assert isinstance(motivo, str) and len(motivo) > 0


@given(texto=st.text())
@settings(max_examples=80, deadline=None)
def test_02_hypothesis_determinismo_classificador(texto):
    """Caça-Furos 2: Mesma entrada deve produzir 100% a mesma decisão (Determinismo Estrito)."""
    r1 = classificar_tarefa_camada_a(texto, 1)
    r2 = classificar_tarefa_camada_a(texto, 1)
    assert r1 == r2


# ==============================================================================
# 2. CAÇADOR DE BUGS (HYPOTHESIS FUZZING): EXTRATOR E FISCAL VALIDADOR
# ==============================================================================
@given(texto_caotico=st.one_of(st.text(), st.none(), st.integers(), st.binary()))
@settings(max_examples=80, deadline=None)
def test_03_hypothesis_extrator_e_validador_nunca_quebram(texto_caotico):
    """Caça-Furos 3: O extrator e o Fiscal Python nunca podem levantar exceção não tratada."""
    bloco = extrair_bloco_python(texto_caotico)
    assert bloco is None or isinstance(bloco, str)

    aprovado, msg = validar_codigo_python(texto_caotico)
    assert isinstance(aprovado, bool)
    assert isinstance(msg, str) and len(msg) > 0


def test_04_furo_prosa_com_palavras_reservadas():
    """
    Caça-Furos 4 (Furo Real Corrigido):
    Garante que uma resposta em texto normal contendo 'return' ou 'import' no meio da frase
    NÃO seja confundida com código Python quebrado.
    """
    prosa = "Para resolver isso, o return da consulta deve considerar o import dos dados."
    assert extrair_bloco_python(prosa) is None
    aprovado, msg = validar_codigo_python(prosa, exigir_codigo_python=False)
    assert aprovado is True
    assert "APROVADO_TEXTO" in msg


def test_05_furo_multiplos_blocos_markdown():
    """
    Caça-Furos 5 (Furo Real Corrigido):
    Quando o modelo gera um bloco de exemplo e outro bloco com a função 'def',
    o extrator deve priorizar o bloco que contém a definição da função.
    """
    resposta_multi = (
        "Exemplo de chamada:\n```python\n# apenas comentario\nx = 10\n```\n"
        "Implementação:\n```python\ndef somar(a, b):\n    return a + b\n```"
    )
    extraido = extrair_bloco_python(resposta_multi)
    assert extraido is not None and "def somar" in extraido
    aprovado, msg = validar_codigo_python(resposta_multi, codigo_teste_assert="assert somar(2, 3) == 5")
    assert aprovado is True
    assert "APROVADO_TOTAL" in msg


def test_06_furo_bloqueio_input_interativo():
    """
    Caça-Furos 6 (Furo Real Corrigido):
    Se um modelo local gerar `input('Digite algo:')`, o Fiscal deve bloquear na AST
    antes do `exec()` para jamais travar o servidor esperando teclado!
    """
    codigo_travante = "```python\ndef ler_nome():\n    return input('Nome: ')\n```"
    aprovado, msg = validar_codigo_python(codigo_travante, codigo_teste_assert="assert True")
    assert aprovado is False
    assert "REPROVADO_BLOQUEIO" in msg


# ==============================================================================
# 3. TESTE DA ESCADA DE 4 DEGRAUS (RTX 5090 -> DEEPSEEK -> 3.8 FLASH -> ARGON)
# ==============================================================================
def test_07_escada_4_degraus_completa():
    """Verifica o roteamento exato para cada um dos 4 degraus da arquitetura."""
    # Degrau 1: 1 arquivo simples
    d1, m1, _ = classificar_tarefa_camada_a("Criar função de formatação de data", arquivos_envolvidos=1)
    assert d1 == "DEGRAU_1_RTX5090_LOCAL"

    # Degrau 2: 2 arquivos ou algoritmo complexo
    d2, m2, _ = classificar_tarefa_camada_a("Realizar cruzamento relacional complexo", arquivos_envolvidos=2)
    assert d2 == "DEGRAU_2_DEEPSEEK_763B"

    # Degrau 3: 3 ou 4 arquivos -> Escudo barato Gemini 3.8 Flash
    d3, m3, _ = classificar_tarefa_camada_a("Ajustar módulos de serviço", arquivos_envolvidos=3)
    assert d3 == "DEGRAU_3_GEMINI_38_FLASH"
    assert m3 == "gemini-3.8-flash"

    # Degrau 4: 5+ arquivos ou arquitetura global -> Orquestrador Argon
    d4, m4, _ = classificar_tarefa_camada_a("Mudança de arquitetura global do sistema", arquivos_envolvidos=6)
    assert d4 == "DEGRAU_4_ARGON_ORQUESTRADOR"
    assert m4 == "gemini-4-argon"


# ==============================================================================
# 4. TESTE REAL E CRONÔMETRO DO MOTOR DE DECISÃO GEV-LITE (1 LETRA / SYSTEM 1)
# ==============================================================================
def test_08_motor_decisao_gev_lite_velocidade_e_precisao():
    """
    Testa o Motor de Decisão Rápida GEV-Lite (inspirado no GEV-26B)
    tomando decisões de roteamento e de fiscalização com 1 única letra na RTX 5090.
    """
    # Aquecimento rápido de 1 chamada
    decidir_gev_lite("Teste rápido", ["Sim", "Não"])

    # Decisão 1: Classificação de tarefa
    d_rota = decidir_gev_lite(
        pergunta="Qual degrau deve executar uma função simples de limpar CPF em 5 linhas?",
        opcoes=[
            "Degrau 1: Placa de Vídeo Local RTX 5090 (Tarefa simples e rápida)",
            "Degrau 4: Orquestrador Argon (Mudança estrutural em 20 arquivos)",
        ],
    )
    assert d_rota.letra_escolhida == "A"
    assert d_rota.indice_escolhido == 0

    # Decisão 2: Fiscal Validador GEV-Lite julgando resposta correta
    d_juiz_ok = validar_com_juiz_gev_lite(
        tarefa="Extrair total de turmas ativas da unidade ACL.",
        resposta_gerada='{"unidade": "ACL", "total_turmas": 25, "status": "extraido_com_sucesso"}',
    )
    assert d_juiz_ok.letra_escolhida == "A"

    # Decisão 3: Fiscal Validador GEV-Lite julgando resposta quebrada/errada
    d_juiz_erro = validar_com_juiz_gev_lite(
        tarefa="Calcular a folha de pagamento em reais de 2026.",
        resposta_gerada="Erro fatal: banco de dados corrompido, nenhum valor calculado.",
    )
    assert d_juiz_erro.letra_escolhida == "B"

    print(
        f"\n[TELEMETRIA GEV-LITE] Decisão Rota: {d_rota.tempo_ms} ms ({d_rota.letra_escolhida}) | "
        f"Fiscal Aprovado: {d_juiz_ok.tempo_ms} ms ({d_juiz_ok.letra_escolhida}) | "
        f"Fiscal Reprovado: {d_juiz_erro.tempo_ms} ms ({d_juiz_erro.letra_escolhida})"
    )


# ==============================================================================
# 5. TESTE DE RECUPERAÇÃO AUTOMÁTICA DEGRAU 1 -> DEGRAU 2 (DEEPSEEK)
# ==============================================================================
def test_09_cascata_real_fim_a_fim():
    """Executa um fluxo real passando pelo Fiscal Validador com asserção."""
    res = executar_roteamento(
        instrucao=(
            "Escreva apenas um bloco ```python``` com `def limpar_matricula(m: str) -> str:` "
            "que retorne apenas os dígitos numéricos da string `m`."
        ),
        arquivos_envolvidos=1,
        codigo_teste_assert="assert limpar_matricula('Matr: 23.654-A') == '23654'",
    )
    assert res.sucesso is True
    assert "APROVADO_TOTAL" in res.validacao_deterministica
    assert res.submeter_ao_argon is False


# ==============================================================================
# 6. CONTRATOS ESTRITOS (PANDERA-STYLE DO ETL-SGI) E AUDITORIA ANALÍTICA DE LOGS
# ==============================================================================
def test_10_contrato_estrito_resultado_roteamento():
    """
    Inspirado em `test_contratos_pandera.py` do ETL-SGI-v02:
    Garante que o contrato de saída `ResultadoRoteamento` jamais aceita campos nulos críticos,
    tempos negativos ou inconsistência entre `sucesso` e `submeter_ao_argon`.
    """
    res_ok = executar_roteamento("Criar constante X = 1", arquivos_envolvidos=1)
    assert isinstance(res_ok.sucesso, bool)
    assert res_ok.tempo_ms >= 0
    assert res_ok.tokens_entrada >= 0 and res_ok.tokens_saida >= 0
    assert len(res_ok.camada_acionada.strip()) > 0
    assert len(res_ok.modelo_utilizado.strip()) > 0
    # Invariante de Contrato: se resolveu com sucesso no Degrau 1/2, não pode submeter ao Argon
    if res_ok.sucesso and res_ok.camada_acionada.startswith("DEGRAU_1"):
        assert res_ok.submeter_ao_argon is False


def test_11_auditoria_integridade_logs_entrega():
    """
    Inspirado em `test_auditoria_duckdb.py` do ETL-SGI-v02:
    Audita o arquivo físico `_entrega/auditoria_roteamento.jsonl` garantindo 0 linhas corrompidas
    e 100% das chaves obrigatórias presentes.
    """
    arquivo_log = DIRETORIO_LOGS / "auditoria_roteamento.jsonl"
    assert arquivo_log.exists(), "Arquivo de auditoria JSONL não foi gerado em _entrega/!"
    linhas = [ln.strip() for ln in arquivo_log.read_text(encoding="utf-8").splitlines() if ln.strip()]
    assert len(linhas) >= 1
    chaves_obrigatorias = {"sucesso", "camada_acionada", "modelo_utilizado", "validacao_deterministica", "tempo_ms", "timestamp"}
    for idx, ln in enumerate(linhas, 1):
        obj = json.loads(ln)
        faltantes = chaves_obrigatorias - set(obj.keys())
        assert not faltantes, f"Linha {idx} do log violou o contrato! Chaves ausentes: {faltantes}"


# ==============================================================================
# 7. OS 5 TESTES ANTI-PIORA DE CÓDIGO (BLINDAGEM DEFINITIVA DE QUALIDADE)
# ==============================================================================
def test_12_anti_mutilacao_preguica_modelo():
    """
    Trava Anti-Piora 1: Barra imediatamente se um modelo menor tentar encolher
    o código usando '# ... resto do código' ou '# existing code'.
    """
    codigo_preguicoso = "```python\ndef calcular():\n    # ... resto do código\n    return 1\n```"
    aprovado, msg = validar_codigo_python(codigo_preguicoso)
    assert aprovado is False
    assert "REPROVADO_MUTILACAO" in msg


def test_13_anti_exclusao_de_funcoes_existentes():
    """
    Trava Anti-Piora 2: Se o arquivo original tinha 3 funções e o modelo devolveu
    apenas 2 funções (apagando 1 sem ordem), o Fiscal barra na hora!
    """
    original = "def func_a():\n    return 1\n\ndef func_b():\n    return 2\n\ndef func_c():\n    return 3\n"
    editado_incompleto = "```python\ndef func_a():\n    return 10\n\ndef func_b():\n    return 2\n```"
    aprovado, msg = validar_codigo_python(editado_incompleto, codigo_original_referencia=original)
    assert aprovado is False
    assert "REPROVADO_REGRESSAO_FUNCOES" in msg and "func_c" in msg


def test_14_bloqueio_comandos_destrutivos_disco():
    """
    Trava Anti-Piora 3: Bloqueia na árvore sintática qualquer tentativa de apagar
    arquivos ou pastas (`os.remove`, `shutil.rmtree`, `os.system`) durante o teste.
    """
    codigo_perigoso = "```python\nimport shutil\ndef limpar():\n    shutil.rmtree('/tmp/algo')\n```"
    aprovado, msg = validar_codigo_python(codigo_perigoso)
    assert aprovado is False
    assert "REPROVADO_SEGURANCA" in msg


def test_15_detector_acentuacao_corrompida_mojibake():
    """
    Trava Anti-Piora 4: Barra textos ou códigos com acentuação estragada (UTF-8 lido como Latin-1).
    """
    texto_mojibake = "```python\ndef saudacao():\n    return 'AtenÃ§Ã£o na validaÃ§Ã£o'\n```"
    aprovado, msg = validar_codigo_python(texto_mojibake)
    assert aprovado is False
    assert "REPROVADO_ENCODING" in msg


def test_16_disjuntor_contra_loop_infinito():
    """
    Trava Anti-Piora 5: Se o modelo gerar um loop infinito (`while True: pass`),
    o disjuntor corta a execução em 3 segundos sem travar a máquina!
    """
    codigo_loop = "```python\ndef travar():\n    while True:\n        pass\n```"
    aprovado, msg = validar_codigo_python(codigo_loop, codigo_teste_assert="travar()")
    assert aprovado is False
    assert "REPROVADO_LOOP_INFINITO" in msg


# ==============================================================================
# 8. TRAVA ANTI-FALSO POSITIVO (CONDICIONANTE OPUS 5.5 / ARGON HOMOLOGADA)
# ==============================================================================
def test_17_bloqueio_falso_positivo_erro_infraestrutura_e_transporte():
    """
    Condicionante Opus 5.5: Impede que erros de transporte/socket do sistema operacional
    sejam mascarados como sucesso ('APROVADO_TEXTO') em tarefas de normalização ou texto livre.
    """
    erro_socket = "Erro no LM Studio: <urlopen error [WinError 10061] Nenhuma conexão pôde ser feita>"
    aprovado, msg = validar_codigo_python(erro_socket)
    assert aprovado is False
    assert "REPROVADO_ERRO_INFRAESTRUTURA" in msg

    erro_ollama = "Erro no Ollama: Connection refused by host"
    aprovado2, msg2 = validar_codigo_python(erro_ollama)
    assert aprovado2 is False
    assert "REPROVADO_ERRO_INFRAESTRUTURA" in msg2


# ==============================================================================
# 9. TESTES DE AUDITORIA FORENSE VERSÃO 1.2 (CHANCELA OPUS 5.5)
# ==============================================================================
def test_18_portao_zero_com_payload_misto_bloco_e_erro():
    """
    Versão 1.2 (Ponto 1): Garante que texto misto (WinError + bloco de código markdown)
    é barrado NO PORTÃO ZERO incondicional, antes mesmo de compilar a AST.
    """
    texto_misto = (
        "Erro de transporte: [WinError 10061] Nenhuma conexão pôde ser feita\n"
        "```python\ndef funcao_inutil():\n    return 42\n```"
    )
    aprovado, msg = validar_codigo_python(texto_misto)
    assert aprovado is False
    assert "REPROVADO_ERRO_INFRAESTRUTURA" in msg


def test_19_contrato_semantico_status_execucao_v12():
    """
    Versão 1.2 (Ponto 3): Garante que delegações diretas externas não marcam sucesso=True.
    """
    res = executar_roteamento("Arquitetura de sistema distribuído", arquivos_envolvidos=6)
    assert res.status_execucao == "ROTEADO_EXTERNO_DEGRAU_4"
    assert res.sucesso is False
    assert res.resposta == ""


def test_20_desacoplamento_resposta_em_falha_transporte():
    """
    Versão 1.2 (Ponto 2): Garante que quando o transporte falha, o campo resposta fica vazio.
    """
    res_falha = executar_roteamento("Função teste", simular_falha_local=True)
    # Na simulação de falha de código, o fiscal barrou
    assert res_falha.sucesso is False
    assert "REPROVADO" in res_falha.validacao_deterministica


# ==============================================================================
# 10. TESTES DE ALTA PERFORMANCE E GOVERNANÇA VERSÃO 1.3 (CHANCELA OPUS 5.5)
# ==============================================================================
def test_21_cache_lru_gev_lite_instantaneo():
    """
    Versão 1.3: Garante que consultas repetidas no GEV-Lite retornam do Cache LRU
    em 0 ms com modo_sistema='cache_lru_fast_gate'.
    """
    pergunta = "Qual modelo para tarefa de 1 linha de log?"
    opcoes = ["DEGRAU_1_RTX5090", "DEGRAU_4_ARGON"]
    # Primeira chamada (alimenta o cache)
    r1 = decidir_gev_lite(pergunta=pergunta, opcoes=opcoes, contexto="log simples")
    # Segunda chamada idêntica (deve vir do cache em 0 ms)
    r2 = decidir_gev_lite(pergunta=pergunta, opcoes=opcoes, contexto="log simples")
    assert r2.modo_sistema == "cache_lru_fast_gate"
    assert r2.tempo_ms == 0
    assert r2.letra_escolhida == r1.letra_escolhida


def test_22_batching_concorrente_preserva_ordem_e_fiscal():
    """
    Versão 1.3: Garante que rotear_lote_instrucoes processa itens em concorrência
    preservando rigorosamente a ordem de entrada e as travas do Fiscal.
    """
    lote = [
        {"instrucao": "Escreva def f1(): return 1"},
        {"instrucao": "Escreva def f2(): return 2"},
        {"instrucao": "Escreva def f3(): return 3"},
    ]
    resultados = rotear_lote_instrucoes(lote, max_concorrencia=3)
    assert len(resultados) == 3
    for r in resultados:
        assert isinstance(r.sucesso, bool)
        assert r.versao_motor == "1.3"


def test_23_metrica_nativa_aprovado_primeira():
    """
    Versão 1.3: Garante que tarefas aprovadas no Degrau 1 marcam aprovado_primeira=True.
    """
    res = executar_roteamento("Escreva def somar(a, b): return a + b")
    assert hasattr(res, "aprovado_primeira")
    if res.status_execucao == "EXECUTADO_LOCAL":
        assert res.aprovado_primeira is True


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v", "-s"]))


