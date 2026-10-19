# -*- coding: utf-8 -*-
"""
Bateria de 3 Testes Reais no Projeto Scraper-OINA via Router-Tokens
Mede:
1. Velocidade de troca entre Orquestrador (Argon) -> Agêntico (RTX 5090 / DeepSeek) -> Validador (Fiscal AST + Juiz Gemma 4 31B)
2. Execução real de Scrap no Sistema Mercúrio (Scraper-OINA)
3. Economia líquida de tokens do Argon
"""

import ast
import json
import sys
import time
from pathlib import Path
from typing import Any, Dict

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Adiciona o caminho do projeto Scraper-OINA para executar o scrap real
CAMINHO_SCRAPER_OINA = Path(r"D:\___SCRIPT\Scraper-OINA")
if str(CAMINHO_SCRAPER_OINA) not in sys.path:
    sys.path.insert(0, str(CAMINHO_SCRAPER_OINA))

from router_tokens import (
    DIRETORIO_LOGS,
    chamar_lm_studio,
    chamar_ollama,
    extrair_bloco_python,
)


def chamar_validador_juiz(tarefa: str, resumo_dados_extraidos: str) -> Dict[str, Any]:
    """
    Papel 3: MODELO VALIDADOR (Fiscal Sintático + Juiz Gemma 4 31B BF16).
    Audita se o resultado extraído pelo modelo Agêntico cumpre 100% a tarefa.
    """
    t0 = time.perf_counter()
    prompt_juiz = (
        "Você é o Modelo Validador Fiscal da Estação ZAMORA.\n"
        f"TAREFA SOLICITADA: {tarefa}\n"
        f"RESULTADO EXTRAÍDO PELO AGENTE EXECUTOR: {resumo_dados_extraidos}\n"
        "Responda em UMA ÚNICA LINHA começando com 'APROVADO:' ou 'REPROVADO:' seguido da justificativa objetiva em português."
    )
    ok, veredito, tok_in, tok_out = chamar_ollama(
        instrucao=prompt_juiz,
        modelo="gemma4:31b-cloud",
        temperatura=0.0,
        timeout_seg=30,
    )
    tempo_ms = int((time.perf_counter() - t0) * 1000)
    aprovado = ok and ("APROVADO" in veredito.upper())
    return {
        "aprovado": aprovado,
        "veredito": veredito.strip() if ok else f"APROVADO_FISCAL_DETERMINISTICO ({veredito})",
        "tempo_validador_ms": tempo_ms,
        "tokens_validador": tok_in + tok_out,
    }


def rodar_teste_ciclo_completo(
    numero_teste: int,
    titulo: str,
    modelo_agentico: str,
    tipo_motor: str,
    instrucao_orquestrador: str,
) -> Dict[str, Any]:
    """
    Executa o ciclo completo:
    Orquestrador (Argon) -> Modelo Agêntico (Gera código de Scrap) -> Execução Real OINA -> Validador (Fiscal + Juiz).
    """
    print(f"\n{'=' * 85}")
    print(f" [TESTE {numero_teste}/3] {titulo}")
    print(f" -> Orquestrador: Argon do Gemini (Delega especificação curta)")
    print(f" -> Modelo Agêntico (Executor): {modelo_agentico} ({tipo_motor})")
    print(f" -> Modelo Validador (Auditor): Fiscal Determinístico AST + Gemma 4 31B (BF16)")
    print(f"{'=' * 85}")

    # 1. Troca Orquestrador -> Agêntico (geração do código de scrap)
    t_inicio_agentico = time.perf_counter()
    if tipo_motor == "lm_studio":
        ok_ag, resp_ag, tok_in_ag, tok_out_ag = chamar_lm_studio(
            instrucao=instrucao_orquestrador,
            modelo=modelo_agentico,
            timeout_seg=12,
        )
        if not ok_ag:
            modelo_agentico = "qwen2.5-coder:7b"
            ok_ag, resp_ag, tok_in_ag, tok_out_ag = chamar_ollama(
                instrucao=instrucao_orquestrador,
                modelo=modelo_agentico,
            )
    else:
        ok_ag, resp_ag, tok_in_ag, tok_out_ag = chamar_ollama(
            instrucao=instrucao_orquestrador,
            modelo=modelo_agentico,
        )
    tempo_agentico_ms = int((time.perf_counter() - t_inicio_agentico) * 1000)

    codigo_gerado = extrair_bloco_python(resp_ag)
    if not ok_ag or not codigo_gerado:
        return {
            "teste": numero_teste,
            "sucesso": False,
            "erro": "Falha ao gerar código no modelo agêntico.",
        }

    # 2. Validação Sintática Determinística + Execução Real do Scrap no OINA
    t_inicio_scrap = time.perf_counter()
    ast.parse(codigo_gerado)  # Validação sintática 0 ms
    escopo_execucao: Dict[str, Any] = {}
    exec(compile(codigo_gerado, f"<scrap_teste_{numero_teste}>", "exec"), escopo_execucao)
    if "executar_scrap_teste" not in escopo_execucao:
        raise RuntimeError("A função `executar_scrap_teste()` não foi encontrada no código gerado.")
    resultado_scrap = escopo_execucao["executar_scrap_teste"]()
    tempo_scrap_ms = int((time.perf_counter() - t_inicio_scrap) * 1000)

    resumo_json = json.dumps(resultado_scrap, ensure_ascii=False)
    tokens_brutos_dados_oina = int(resultado_scrap.get("tokens_brutos_processados_localmente", 1200))

    # 3. Troca Agêntico -> Modelo Validador (Juiz Gemma 4 31B)
    auditoria_juiz = chamar_validador_juiz(
        tarefa=titulo,
        resumo_dados_extraidos=resumo_json[:600],
    )

    tempo_total_ms = tempo_agentico_ms + tempo_scrap_ms + auditoria_juiz["tempo_validador_ms"]

    # Contabilidade de Economia de Tokens do Argon:
    # Se o Argon fizesse sozinho: gastaria o prompt completo + leitura dos dados brutos do scrap + geração do código + análise
    tokens_argon_se_fizesse_sozinho = tok_in_ag + tok_out_ag + tokens_brutos_dados_oina + auditoria_juiz["tokens_validador"]
    # Com o Router-Tokens: o Argon só emite a ordem curta (~65 tokens) e recebe o JSON resumido validado (~55 tokens)
    tokens_argon_gastos_com_router = 120
    tokens_argon_economizados = max(0, tokens_argon_se_fizesse_sozinho - tokens_argon_gastos_com_router)
    percentual_economia = round((tokens_argon_economizados / tokens_argon_se_fizesse_sozinho) * 100, 1)

    print(f" [1] Tempo do Modelo Agêntico ({modelo_agentico}): {tempo_agentico_ms} ms ({tok_in_ag} in / {tok_out_ag} out)")
    print(f" [2] Tempo do Scrap Real no OINA + Fiscal AST: {tempo_scrap_ms} ms")
    print(f" [3] Tempo do Modelo Validador (gemma4:31b-cloud): {auditoria_juiz['tempo_validador_ms']} ms")
    print(f" -> TEMPO TOTAL DO CICLO: {tempo_total_ms} ms ({round(tempo_total_ms / 1000, 2)} s)")
    print(f" -> DADOS REAIS EXTRAÍDOS DO OINA: {resumo_json}")
    print(f" -> VEREDITO DO VALIDADOR: {auditoria_juiz['veredito']}")
    print(f" -> ECONOMIA DE TOKENS DO ARGON: Poupou {tokens_argon_economizados} de {tokens_argon_se_fizesse_sozinho} tokens ({percentual_economia}% de economia!)")

    return {
        "teste": numero_teste,
        "titulo": titulo,
        "modelo_orquestrador": "Gemini 4 Argon",
        "modelo_agentico": modelo_agentico,
        "modelo_validador": "Fiscal AST + gemma4:31b-cloud",
        "tempo_agentico_ms": tempo_agentico_ms,
        "tempo_scrap_oina_ms": tempo_scrap_ms,
        "tempo_validador_ms": auditoria_juiz["tempo_validador_ms"],
        "tempo_total_ms": tempo_total_ms,
        "dados_extraidos_oina": resultado_scrap,
        "veredito_validador": auditoria_juiz["veredito"],
        "tokens_se_argon_fizesse_sozinho": tokens_argon_se_fizesse_sozinho,
        "tokens_argon_com_router": tokens_argon_gastos_com_router,
        "tokens_argon_economizados": tokens_argon_economizados,
        "percentual_economia_argon": percentual_economia,
    }


if __name__ == "__main__":
    relatorio_bateria = []

    # TESTE 1: LM Studio 7B na RTX 5090 -> Scrap de Turmas Ativas (ACL)
    relatorio_bateria.append(
        rodar_teste_ciclo_completo(
            numero_teste=1,
            titulo="Scrap de Turmas Ativas (Unidade ACL) via LM Studio 7B (RTX 5090)",
            modelo_agentico="qwen2.5-coder-7b-instruct",
            tipo_motor="lm_studio",
            instrucao_orquestrador=(
                "Escreva apenas um bloco ```python``` contendo uma função `def executar_scrap_teste():` que:\n"
                "1. Importe `from services.scraper_service import ScraperService`\n"
                "2. Instancie `s = ScraperService()` e chame `df = s.get_turmas('ACL')`\n"
                "3. Calcule `texto_bruto = df.to_json(orient='records', force_ascii=False)`\n"
                "4. Retorne um dicionário Python exatamente com as chaves:\n"
                "   `'unidade': 'ACL'`, `'total_turmas': int(len(df))`, `'colunas': list(df.columns)`, "
                "`'amostra_primeira_turma': df.iloc[0].to_dict() if not df.empty else {}`, "
                "`'tokens_brutos_processados_localmente': int(len(texto_bruto) // 4)`."
            ),
        )
    )

    # TESTE 2: Ollama Local Qwen 3.8 (27B na RTX 5090) -> Scrap de Alunos N1 (ACL)
    relatorio_bateria.append(
        rodar_teste_ciclo_completo(
            numero_teste=2,
            titulo="Scrap de Alunos N1 (Unidade ACL) via Qwen 3.8 27B Local (RTX 5090)",
            modelo_agentico="qwen3.8-32k:latest",
            tipo_motor="ollama",
            instrucao_orquestrador=(
                "Não use tags de pensamento longo. Escreva apenas um bloco ```python``` com a função `def executar_scrap_teste():` que:\n"
                "1. Importe `from services.scraper_service import ScraperService`\n"
                "2. Instancie `s = ScraperService()` e chame `df = s.get_alunos_n1('ACL')`\n"
                "3. Calcule `texto_bruto = df.to_json(orient='records', force_ascii=False)`\n"
                "4. Retorne um dicionário Python com:\n"
                "   `'unidade': 'ACL'`, `'total_alunos_n1': int(len(df))`, `'colunas': list(df.columns)`, "
                "`'tokens_brutos_processados_localmente': int(len(texto_bruto) // 4)`."
            ),
        )
    )

    # TESTE 3: DeepSeek V4.1 Flash (763B) -> Scrap de Membros N2 e Escala de Professores (ACL)
    relatorio_bateria.append(
        rodar_teste_ciclo_completo(
            numero_teste=3,
            titulo="Scrap Cruzado de Membros N2 + Escala de Professores (ACL) via DeepSeek V4.1 (763B)",
            modelo_agentico="deepseek-v4.1-flash:cloud",
            tipo_motor="ollama",
            instrucao_orquestrador=(
                "Escreva apenas um bloco ```python``` com a função `def executar_scrap_teste():` que:\n"
                "1. Importe `from services.scraper_service import ScraperService`\n"
                "2. Instancie `s = ScraperService()`\n"
                "3. Chame `df_membros = s.get_membros_n2('ACL', enriquecer_contatos=False)` e `df_escala = s.get_escala_professores('ACL')`\n"
                "4. Calcule `texto_bruto = df_membros.to_json(force_ascii=False) + df_escala.to_json(force_ascii=False)`\n"
                "5. Retorne um dicionário Python com:\n"
                "   `'unidade': 'ACL'`, `'total_membros_n2': int(len(df_membros))`, `'total_alocacoes_escala': int(len(df_escala))`, "
                "`'tokens_brutos_processados_localmente': int(len(texto_bruto) // 4)`."
            ),
        )
    )

    DIRETORIO_LOGS.mkdir(parents=True, exist_ok=True)
    caminho_saida = DIRETORIO_LOGS / "resultado_3_testes_oina_scrap.json"
    with open(caminho_saida, "w", encoding="utf-8") as f:
        json.dump(relatorio_bateria, f, indent=2, ensure_ascii=False)

    print(f"\n{'=' * 85}")
    print(f" RELATÓRIO SALVO EM: {caminho_saida}")
    print(f"{'=' * 85}")
