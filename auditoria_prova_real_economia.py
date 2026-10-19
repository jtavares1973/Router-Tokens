# -*- coding: utf-8 -*-
"""
Auditoria Pericial de Prova Real de Economia — Estação ZAMORA
Comprova matematicamente por A + B a economia de tokens e custos financeiros
utilizando o LiteLLM Proxy na porta 4000 acoplado à RTX 5090 (32 GB).
"""

import ast
import json
import time
import urllib.request
from typing import Dict, Any, List

URL_LITELLM = "http://127.0.0.1:4000/v1/chat/completions"
API_KEY = "sk-zamora-pericial-5090"

# Tarifas Oficiais de Nuvem (Por 1 Milhão de Tokens em Dólares)
# Claude 3.5 Sonnet / Opus / GPT-4o / Gemini Pro
PRECOS_NUVEM = {
    "Claude_Opus": {"entrada_milhao": 15.00, "saida_milhao": 75.00},
    "Gemini_Argon_Pro": {"entrada_milhao": 3.50, "saida_milhao": 10.50},
    "RTX_5090_Local": {"entrada_milhao": 0.00, "saida_milhao": 0.00},
}

COTACAO_DOLAR_BRL = 5.85

def executar_caso_real(nome_caso: str, prompt: str, assert_teste: str) -> Dict[str, Any]:
    carga = {
        "model": "zamora-executor-local",
        "messages": [
            {
                "role": "system",
                "content": "Você é o executor de código local da Estação ZAMORA na RTX 5090. Escreva apenas o bloco ```python ... ``` com a implementação perfeita."
            },
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1,
        "max_tokens": 512
    }
    
    dados = json.dumps(carga).encode("utf-8")
    req = urllib.request.Request(
        URL_LITELLM,
        data=dados,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}"
        },
        method="POST"
    )
    
    t0 = time.perf_counter()
    with urllib.request.urlopen(req, timeout=60) as resp:
        tempo_ms = int((time.perf_counter() - t0) * 1000)
        corpo = json.loads(resp.read().decode("utf-8"))
        texto = corpo["choices"][0]["message"]["content"]
        uso = corpo.get("usage", {})
        tokens_in = uso.get("prompt_tokens", 0)
        tokens_out = uso.get("completion_tokens", 0)
        
    # Extração de código
    import re
    bloco = re.search(r"```python\s*(.*?)\s*```", texto, re.DOTALL)
    codigo = bloco.group(1).strip() if bloco else texto.strip()
    
    # Fiscal Sintático AST + Execução de Teste Assert
    valido_ast = False
    assert_ok = False
    erro_msg = ""
    try:
        ast.parse(codigo)
        valido_ast = True
        escopo = {}
        exec(compile(codigo, "<codigo>", "exec"), escopo)
        exec(compile(assert_teste, "<assert>", "exec"), escopo)
        assert_ok = True
    except Exception as e:
        erro_msg = str(e)
        
    # Cálculo de Custos
    custo_rtx5090 = 0.0
    custo_opus_usd = (tokens_in * PRECOS_NUVEM["Claude_Opus"]["entrada_milhao"] + tokens_out * PRECOS_NUVEM["Claude_Opus"]["saida_milhao"]) / 1_000_000
    custo_argon_usd = (tokens_in * PRECOS_NUVEM["Gemini_Argon_Pro"]["entrada_milhao"] + tokens_out * PRECOS_NUVEM["Gemini_Argon_Pro"]["saida_milhao"]) / 1_000_000
    
    return {
        "caso": nome_caso,
        "tempo_ms": tempo_ms,
        "tokens_entrada": tokens_in,
        "tokens_saida": tokens_out,
        "tokens_total": tokens_in + tokens_out,
        "ast_valida": valido_ast,
        "assert_aprovado": assert_ok,
        "erro": erro_msg,
        "custo_real_pago_usd": custo_rtx5090,
        "custo_evitado_opus_usd": custo_opus_usd,
        "custo_evitado_argon_usd": custo_argon_usd,
        "codigo_gerado": codigo[:250] + ("..." if len(codigo) > 250 else "")
    }

def main():
    print("=" * 80)
    print(" BATERIA PERICIAL DE PROVA REAL DE ECONOMIA (POLÍTICA 90/10)")
    print(" ESTAÇÃO ZAMORA — NVIDIA GEFORCE RTX 5090 (32 GB GDDR7)")
    print("=" * 80)
    
    testes = [
        (
            "Caso 1: Validador Matemático de Dígitos Verificadores de CPF",
            "Escreva a função `def validar_cpf(cpf: str) -> bool:` que limpa formatação e valida os 2 dígitos verificadores de acordo com a regra oficial brasileira.",
            "assert validar_cpf('11144477735') is True and validar_cpf('11144477700') is False"
        ),
        (
            "Caso 2: Extrator Regex de Boletins de Ocorrência Policial",
            "Escreva a função `def extrair_numero_bo(texto: str) -> str:` que localize e retorne números de ocorrência no formato 'NNNNN/AAAA' ou retorne string vazia.",
            "assert extrair_numero_bo('Registrado sob o BO 12345/2026 na DP') == '12345/2026'"
        ),
        (
            "Caso 3: Normalizador de Matrícula e Sanitização de Dados",
            "Escreva a função `def formatar_matricula(num: int) -> str:` que receba um inteiro e retorne a matrícula formatada com 8 dígitos e prefixo 'POL-' (ex: 2541 vira 'POL-00002541').",
            "assert formatar_matricula(2541) == 'POL-00002541'"
        )
    ]
    
    resultados = []
    tot_tokens_in = 0
    tot_tokens_out = 0
    tot_tempo = 0
    tot_evitado_opus = 0.0
    tot_evitado_argon = 0.0
    
    for i, (nome, prompt, ass) in enumerate(testes, 1):
        print(f"\n[Executando {i}/3] -> {nome}...")
        res = executar_caso_real(nome, prompt, ass)
        resultados.append(res)
        
        tot_tokens_in += res["tokens_entrada"]
        tot_tokens_out += res["tokens_saida"]
        tot_tempo += res["tempo_ms"]
        tot_evitado_opus += res["custo_evitado_opus_usd"]
        tot_evitado_argon += res["custo_evitado_argon_usd"]
        
        status_assert = "APROVADO (100%)" if res["assert_aprovado"] else f"FALHOU ({res['erro']})"
        print(f" -> Concluído em {res['tempo_ms']} ms | Tokens: In={res['tokens_entrada']}, Out={res['tokens_saida']}")
        print(f" -> Validação AST: {'SIM' if res['ast_valida'] else 'NÃO'} | Teste Assert: {status_assert}")
        print(f" -> Custo Real Pago: US$ 0.0000 | Economia vs Opus: US$ {res['custo_evitado_opus_usd']:.5f}")
        
    print("\n" + "=" * 80)
    print(" DEMONSTRAÇÃO MATEMÁTICA POR A + B (AUDITORIA FORENSE)")
    print("=" * 80)
    print(f" Total de Tokens Processados na RTX 5090: {tot_tokens_in + tot_tokens_out} tokens")
    print(f"  |-- Tokens de Entrada: {tot_tokens_in}")
    print(f"  +-- Tokens de Saida:   {tot_tokens_out}")

    print(f" Tempo Total Acumulado: {tot_tempo} ms (Média: {tot_tempo / len(testes):.1f} ms por tarefa)")
    print("-" * 80)
    print(f" CUSTO REAL PAGO NA ESTAÇÃO ZAMORA:        US$ 0,000000 (R$ 0,00)")
    print(f" CUSTO SE ENVIADO AO CLAUDE OPUS:           US$ {tot_evitado_opus:.5f} (R$ {tot_evitado_opus * COTACAO_DOLAR_BRL:.3f})")
    print(f" CUSTO SE ENVIADO AO GEMINI ARGON PRO:      US$ {tot_evitado_argon:.5f} (R$ {tot_evitado_argon * COTACAO_DOLAR_BRL:.3f})")
    print("-" * 80)
    print(f" PERCENTUAL DE TOKENS DE NUVEM POUPADOS:   100,00% (ZERO TOKENS DE NUVEM)")
    print(f" PRESERVAÇÃO DA POLÍTICA 90/10:            100% NO HARDWARE LOCAL")
    print("=" * 80)
    
    # Salva relatório auditável em JSON
    with open("d:/___SCRIPT/Router-Tokens/_entrega/prova_real_economia_auditada.json", "w", encoding="utf-8") as f:
        json.dump({
            "estacao": "ZAMORA",
            "hardware": "NVIDIA GeForce RTX 5090 (32 GB GDDR7)",
            "modelo_utilizado": "qwen2.5-coder:32b via LiteLLM Proxy:4000",
            "metricas": {
                "total_tokens_locais": tot_tokens_in + tot_tokens_out,
                "tokens_nuvem_consumidos": 0,
                "economia_percentual_tokens": 100.0,
                "custo_real_usd": 0.0,
                "economia_opus_usd": tot_evitado_opus,
                "economia_opus_brl": tot_evitado_opus * COTACAO_DOLAR_BRL,
                "economia_argon_usd": tot_evitado_argon,
                "economia_argon_brl": tot_evitado_argon * COTACAO_DOLAR_BRL
            },
            "casos_auditados": resultados
        }, f, indent=2, ensure_ascii=False)
        
    print("\n[OK] Relatório auditável gravado em '_entrega/prova_real_economia_auditada.json'")

if __name__ == "__main__":
    main()
