# -*- coding: utf-8 -*-
"""
Bateria Progressiva de Testes: Do Mais Simples ao Mais Complexo
Projeto Router-Tokens — Estação ZAMORA (RTX 5090 + LiteLLM + Política 90/10)
"""

import ast
import json
import time
import urllib.request
from typing import Dict, Any

from router_tokens import (
    decidir_gev_lite,
    executar_roteamento,
    validar_codigo_python,
    classificar_tarefa_camada_a,
)

def executar_bateria_progressiva():
    print("=" * 80)
    print(" BATERIA PROGRESSIVA DO ROTEADOR: DO MAIS SIMPLES AO MAIS COMPLEXO")
    print(" ESTAÇÃO ZAMORA — NVIDIA GEFORCE RTX 5090 (32 GB) + ESCADA 4 DEGRAUS")
    print("=" * 80)
    
    resultados = []
    
    # -------------------------------------------------------------------------
    # NÍVEL 1: ULTRASSIMPLES (Motor de Decisão GEV-Lite na RTX 5090 - Milissegundos)
    # -------------------------------------------------------------------------
    print("\n[NÍVEL 1: ULTRASSIMPLES] Decisão Instantânea GEV-Lite (1 Token na RTX 5090)")
    t0 = time.perf_counter()
    decisao = decidir_gev_lite(
        pergunta="Qual o destino de uma rotina simples de limpar espaço em string?",
        opcoes=[
            "Degrau 1: RTX 5090 Local (Custo Zero, 24 ms)",
            "Degrau 4: Orquestrador Nuvem (Caro e Desnecessário)"
        ]
    )
    t_ms = int((time.perf_counter() - t0) * 1000)
    assert decisao.letra_escolhida == "A", f"Esperado 'A', obtido '{decisao.letra_escolhida}'"
    print(f" -> Letra Decidida: [{decisao.letra_escolhida}] -> {decisao.opcao_escolhida}")
    print(f" -> Tempo: {t_ms} ms | Modo: {decisao.modo_sistema} | Modelo: {decisao.modelo_decisor}")
    print(" -> Status: APROVADO COM LOUVOR")
    resultados.append({"nivel": "Nível 1 (Ultrassimples)", "tempo_ms": t_ms, "status": "APROVADO", "degrau": "Degrau 1 (GEV-Lite)"})
    
    # -------------------------------------------------------------------------
    # NÍVEL 2: BÁSICO (Execução de Código Atômico no Degrau 1 - RTX 5090 Local)
    # -------------------------------------------------------------------------
    print("\n[NÍVEL 2: BÁSICO] Execução de Função Atômica Local na RTX 5090")
    t0 = time.perf_counter()
    res_n2 = executar_roteamento(
        instrucao="Escreva uma função ```python def normalizar_rg(rg: str) -> str:``` que retorne apenas dígitos numéricos de rg.",
        arquivos_envolvidos=1,
        codigo_teste_assert="assert normalizar_rg('SSP-12.345.678-X') == '12345678'"
    )
    t_ms = int((time.perf_counter() - t0) * 1000)
    print(f" -> Camada Acionada: {res_n2.camada_acionada} ({res_n2.modelo_utilizado})")
    print(f" -> Validação Determinística: {res_n2.validacao_deterministica}")
    print(f" -> Tempo: {res_n2.tempo_ms} ms | Custo Nuvem: US$ {res_n2.custo_estimado_usd:.4f}")
    assert res_n2.sucesso is True, f"Falha no Nível 2: {res_n2.resposta}"
    print(" -> Status: APROVADO COM LOUVOR")
    resultados.append({"nivel": "Nível 2 (Básico)", "tempo_ms": res_n2.tempo_ms, "status": "APROVADO", "degrau": res_n2.camada_acionada})
    
    # -------------------------------------------------------------------------
    # NÍVEL 3: INTERMEDIÁRIO (Fiscal Anti-Piora Barrando Código Mutilado)
    # -------------------------------------------------------------------------
    print("\n[NÍVEL 3: INTERMEDIÁRIO] Blindagem Anti-Piora (Detector de Código Mutilado/Preguiçoso)")
    codigo_preguicoso = "def processar_inquerito():\n    # ... resto do codigo vem aqui\n    return True"
    aprovado, msg = validar_codigo_python(codigo_preguicoso)
    print(f" -> Submetido código com '# ... resto do codigo'")
    print(f" -> Veredito do Fiscal: Aprovado={aprovado} | Mensagem: {msg}")
    assert aprovado is False and "REPROVADO_MUTILACAO" in msg
    print(" -> Status: APROVADO (Fiscal barrou com precisão cirúrgica)")
    resultados.append({"nivel": "Nível 3 (Intermediário - Fiscal)", "tempo_ms": 0, "status": "APROVADO (Barrou mutilação)", "degrau": "Fiscal AST (0 ms)"})
    
    # -------------------------------------------------------------------------
    # NÍVEL 4: AVANÇADO (Tarefa Densa / Algorítmica no Degrau 2 - DeepSeek 763B)
    # -------------------------------------------------------------------------
    print("\n[NÍVEL 4: AVANÇADO] Tarefa Analítica / Cruzamento de Dados (Degrau 2 - DeepSeek 763B)")
    camada, modelo, motivo = classificar_tarefa_camada_a(
        instrucao="Desenvolva algoritmo complexo de cruzamento relacional e auditoria forense de ocorrências",
        arquivos_envolvidos=2
    )
    print(f" -> Classificação Automática: {camada} -> {modelo}")
    print(f" -> Motivo da Rota: {motivo}")
    assert camada == "DEGRAU_2_DEEPSEEK_763B", f"Esperado Degrau 2, obtido {camada}"
    print(" -> Status: APROVADO (Roteamento inteligente para Degrau 2)")
    resultados.append({"nivel": "Nível 4 (Avançado)", "tempo_ms": 0, "status": "APROVADO", "degrau": "Degrau 2 (DeepSeek 763B)"})
    
    # -------------------------------------------------------------------------
    # NÍVEL 5: MÁXIMA COMPLEXIDADE (Projeto Sistêmico no Degrau 4 - Orquestrador Argon)
    # -------------------------------------------------------------------------
    print("\n[NÍVEL 5: MÁXIMA COMPLEXIDADE] Projeto Arquitetural Estratégico (Degrau 4 - Orquestrador Argon)")
    res_n5 = executar_roteamento(
        instrucao="Arquitetura de microsserviços distribuídos para o sistema procedural da PCDF em múltiplos módulos",
        arquivos_envolvidos=6
    )
    print(f" -> Camada Acionada: {res_n5.camada_acionada}")
    print(f" -> Diagnóstico: {res_n5.diagnostico_escalonamento}")
    print(f" -> Submeter ao Argon: {res_n5.submeter_ao_argon}")
    assert res_n5.submeter_ao_argon is True and "DEGRAU_4" in res_n5.camada_acionada
    print(" -> Status: APROVADO (Contenção restrita a 10% cumprida)")
    resultados.append({"nivel": "Nível 5 (Máxima Complexidade)", "tempo_ms": res_n5.tempo_ms, "status": "APROVADO", "degrau": "Degrau 4 (Argon/Opus)"})
    
    # -------------------------------------------------------------------------
    # QUADRO CONSOLIDADO DE HOMOLOGAÇÃO
    # -------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print(" TABELA CONSOLIDADA DA BATERIA PROGRESSIVA (5 NÍVEIS HOMOLOGADOS)")
    print("=" * 80)
    for r in resultados:
        print(f" [{r['nivel']}] -> Degrau: {r['degrau']} | Status: {r['status']}")
    print("=" * 80)
    print(" CONCLUSÃO PERICIAL: O ROTEADOR ESTÁ 100% OPERACIONAL E FUNCIONANDO!")
    print("=" * 80)

if __name__ == "__main__":
    executar_bateria_progressiva()
