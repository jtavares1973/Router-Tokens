# -*- coding: utf-8 -*-
"""
Servidor MCP Oficial do Router-Tokens (Política 90/10 + GEV-Lite)
Permite acionar a Escada de 4 Degraus e o Motor de Decisão Rápida GEV-Lite
a partir de qualquer projeto ou IDE compatível com MCP.
"""

import json
from mcp.server.fastmcp import FastMCP
from router_tokens import (
    classificar_tarefa_camada_a,
    decidir_gev_lite,
    executar_roteamento,
    validar_codigo_python,
    validar_com_juiz_gev_lite,
)

mcp = FastMCP("Router-Tokens")


@mcp.tool()
def rotear_tarefa_codigo(
    instrucao: str,
    arquivos_envolvidos: int = 1,
    codigo_teste_assert: str = "",
) -> str:
    """
    Executa uma tarefa na Escada de 4 Degraus (RTX 5090 Local -> DeepSeek 763B -> 3.8 Flash -> Argon)
    com validação automática do Fiscal Anti-Piora.
    """
    res = executar_roteamento(
        instrucao=instrucao,
        arquivos_envolvidos=arquivos_envolvidos,
        codigo_teste_assert=codigo_teste_assert.strip() or None,
    )
    return json.dumps(res.__dict__, indent=2, ensure_ascii=False)


@mcp.tool()
def decidir_rapido_gev(pergunta: str, opcoes_separadas_por_ponto_virgula: str, contexto: str = "") -> str:
    """
    Motor de Decisão Instantânea GEV-Lite (24 a 37 ms):
    Decide entre opções (separadas por ';') respondendo com 1 única letra (A, B, C...).
    """
    lista_opcoes = [op.strip() for op in opcoes_separadas_por_ponto_virgula.split(";") if op.strip()]
    res = decidir_gev_lite(pergunta=pergunta, opcoes=lista_opcoes, contexto=contexto)
    return json.dumps(res.__dict__, indent=2, ensure_ascii=False)


@mcp.tool()
def fiscalizar_codigo_anti_piora(
    codigo_gerado: str,
    codigo_teste_assert: str = "",
    codigo_original_referencia: str = "",
) -> str:
    """
    Passa um código pelo Fiscal Validador (Portão AST + 5 Travas Anti-Piora + Juiz GEV-Lite).
    """
    aprovado, msg = validar_codigo_python(
        texto_resposta=codigo_gerado,
        codigo_teste_assert=codigo_teste_assert.strip() or None,
        codigo_original_referencia=codigo_original_referencia.strip() or None,
    )
    juiz = validar_com_juiz_gev_lite("Validar integridade do código", codigo_gerado)
    return json.dumps(
        {
            "aprovado_fiscal_deterministico": aprovado,
            "mensagem_fiscal": msg,
            "veredito_gev_lite": juiz.letra_escolhida,
            "tempo_gev_ms": juiz.tempo_ms,
        },
        indent=2,
        ensure_ascii=False,
    )


if __name__ == "__main__":
    mcp.run()
