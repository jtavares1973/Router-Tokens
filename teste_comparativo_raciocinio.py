# -*- coding: utf-8 -*-
"""
Teste Comparativo Pericial: Modelo Preditivo vs. Modelo Raciocinador na RTX 5090
Estação ZAMORA — Comparativo de Capacidade Cognitiva Local

Avalia:
1. Qwen2.5-Coder:32B (Geração Direta / Predição Pura)
2. DeepSeek-R1:32B (Raciocínio Profundo / Cadeia de Pensamento Test-Time Compute)

Desafio Lógico:
Construção de uma função de reconciliação de transações financeiras com janela deslizante,
tratamento de duplicidades atômicas e ordenação por prioridade de carimbo de tempo.
"""

import json
import time
import urllib.request
import ast
import os

URL_OLLAMA = "http://127.0.0.1:11434/api/chat"

PROMPT_DESAFIO = (
    "Você é um engenheiro sênior de software pericial. "
    "Escreva uma função Python chamada 'reconciliar_transacoes(extrato_a, extrato_b, tolerancia_segundos=5)' "
    "que receba duas listas de dicionários com chaves {'id': str, 'valor': float, 'timestamp': float}. "
    "A função deve casar pares de transações de extrato_a e extrato_b que tenham o MESMO valor absoluto "
    "(diferença <= 0.001) e cujo timestamp esteja dentro da janela de tolerancia_segundos. "
    "Cada transação só pode ser casada no máximo UMA vez (sem casamento duplicado). "
    "Em caso de empate de candidatos válidos, priorize a transação com a menor diferença temporal absoluta. "
    "Retorne uma tupla: (lista_casadas, nao_casadas_a, nao_casadas_b), onde lista_casadas é uma lista de tuplas (transacao_a, transacao_b). "
    "Responda estritamente com o bloco de código Python sem explicações preliminares."
)

def consultar_modelo(nome_modelo: str, prompt: str):
    print(f"\n=======================================================")
    print(f" Consultando: {nome_modelo} na RTX 5090...")
    print(f"=======================================================")
    
    payload = {
        "model": nome_modelo,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "stream": False,
        "options": {
            "temperature": 0.2
        }
    }
    
    dados = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        URL_OLLAMA,
        data=dados,
        headers={"Content-Type": "application/json"}
    )
    
    t0 = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            duracao_s = time.perf_counter() - t0
            resposta = json.loads(resp.read().decode("utf-8"))
            mensagem = resposta.get("message", {})
            conteudo = mensagem.get("content", "")
            pensamento = mensagem.get("thinking", "")
            
            # Se vier dentro de tags <think> no conteúdo
            if "<think>" in conteudo and "</think>" in conteudo:
                partes = conteudo.split("</think>")
                pensamento = partes[0].replace("<think>", "").strip()
                conteudo = partes[1].strip()
            
            tps = resposta.get("eval_count", 0) / (resposta.get("eval_duration", 1) / 1e9)
            
            print(f" [Tempo de Inferência]: {duracao_s:.2f} s")
            print(f" [Velocidade]:          {tps:.1f} tokens/s")
            print(f" [Tokens de Resposta]:  {resposta.get('eval_count', 0)}")
            if pensamento:
                print(f" [Tamanho do Pensamento]: {len(pensamento)} caracteres")
                print(f" [Prévia do Raciocínio]: {pensamento[:250]}...")
            
            # Extração limpa do bloco Python
            bloco_codigo = conteudo
            if "```python" in conteudo:
                bloco_codigo = conteudo.split("```python")[1].split("```")[0].strip()
            elif "```" in conteudo:
                bloco_codigo = conteudo.split("```")[1].split("```")[0].strip()
                
            # Validação Sintática com AST
            valido_ast = False
            try:
                ast.parse(bloco_codigo)
                valido_ast = True
            except Exception as e:
                valido_ast = False
                
            print(f" [Validação Sintática AST]: {'APROVADA' if valido_ast else 'FALHA'}")
            
            return {
                "modelo": nome_modelo,
                "duracao_s": duracao_s,
                "tokens": resposta.get("eval_count", 0),
                "tps": tps,
                "pensamento_presente": bool(pensamento),
                "pensamento_resumo": pensamento[:300] if pensamento else "",
                "valido_ast": valido_ast,
                "codigo": bloco_codigo
            }
    except Exception as erro:
        print(f" [ERRO]: {erro}")
        return {"modelo": nome_modelo, "erro": str(erro)}

def testar_execucao_funcional(codigo_str: str) -> dict:
    """Executa o código gerado em ambiente isolado e testa casos de borda reais."""
    escopo = {}
    try:
        exec(codigo_str, escopo)
        func = escopo.get("reconciliar_transacoes")
        if not func:
            return {"sucesso": False, "motivo": "Função 'reconciliar_transacoes' não encontrada"}
        
        # Caso de Teste 1: Empate com menor diferença temporal
        # Transação A (R$ 100, t=10) deve casar com B2 (R$ 100, t=11, dif=1) e NÃO com B1 (R$ 100, t=14, dif=4)
        extrato_a = [{"id": "A1", "valor": 100.0, "timestamp": 10.0}]
        extrato_b = [
            {"id": "B1", "valor": 100.0, "timestamp": 14.0},
            {"id": "B2", "valor": 100.0, "timestamp": 11.0}
        ]
        
        casadas, n_a, n_b = func(extrato_a, extrato_b, tolerancia_segundos=5)
        
        assert len(casadas) == 1, f"Deveria ter 1 casada, obteve {len(casadas)}"
        par = casadas[0]
        id_b_casado = par[1]["id"]
        assert id_b_casado == "B2", f"Deveria priorizar menor diferença temporal B2, mas casou com {id_b_casado}"
        assert len(n_a) == 0, "Extrato A deveria ter 0 não casadas"
        assert len(n_b) == 1 and n_b[0]["id"] == "B1", "Extrato B deveria ter B1 como não casada"
        
        # Caso de Teste 2: Janela fora do limite
        extrato_fora_a = [{"id": "A2", "valor": 50.0, "timestamp": 10.0}]
        extrato_fora_b = [{"id": "B3", "valor": 50.0, "timestamp": 20.0}] # dif = 10s > tol 5s
        casadas2, n_a2, n_b2 = func(extrato_fora_a, extrato_fora_b, tolerancia_segundos=5)
        assert len(casadas2) == 0, "Transação fora do prazo não deveria casar"
        assert len(n_a2) == 1 and len(n_b2) == 1, "Ambas deveriam ficar como não casadas"
        
        return {"sucesso": True, "motivo": "Todos os testes de casos de borda foram aprovados com sucesso!"}
    except Exception as e:
        return {"sucesso": False, "motivo": f"Falha na validação funcional: {e}"}

def main():
    print("=" * 70)
    print(" BATALHA COGNITIVA NA RTX 5090: PREDITIVO vs. RACIOCINADOR")
    print("=" * 70)
    
    # 1. Testar Modelo Preditivo
    res_qwen = consultar_modelo("qwen2.5-coder:32b", PROMPT_DESAFIO)
    teste_func_qwen = testar_execucao_funcional(res_qwen.get("codigo", ""))
    print(f" [Teste Funcional Qwen]: {'SUCESSO' if teste_func_qwen['sucesso'] else 'REPROVADO'}")
    print(f"  -> Detalhe: {teste_func_qwen['motivo']}")
    
    # 2. Testar Modelo Raciocinador
    res_r1 = consultar_modelo("deepseek-r1:32b", PROMPT_DESAFIO)
    teste_func_r1 = testar_execucao_funcional(res_r1.get("codigo", ""))
    print(f" [Teste Funcional DeepSeek-R1]: {'SUCESSO' if teste_func_r1['sucesso'] else 'REPROVADO'}")
    print(f"  -> Detalhe: {teste_func_r1['motivo']}")
    
    relatorio = {
        "data": time.strftime("%Y-%m-%d %H:%M:%S"),
        "desafio": "Reconciliação com janela temporal deslizante e empate de menor delta t",
        "qwen2_5_coder_32b": {
            "duracao_s": res_qwen.get("duracao_s"),
            "tokens": res_qwen.get("tokens"),
            "tps": res_qwen.get("tps"),
            "valido_ast": res_qwen.get("valido_ast"),
            "teste_funcional": teste_func_qwen
        },
        "deepseek_r1_32b": {
            "duracao_s": res_r1.get("duracao_s"),
            "tokens": res_r1.get("tokens"),
            "tps": res_r1.get("tps"),
            "pensamento_presente": res_r1.get("pensamento_presente"),
            "resumo_pensamento": res_r1.get("pensamento_resumo"),
            "valido_ast": res_r1.get("valido_ast"),
            "teste_funcional": teste_func_r1
        }
    }
    
    os.makedirs("_entrega", exist_ok=True)
    caminho_out = os.path.join("_entrega", "comparativo_raciocinio_5090.json")
    with open(caminho_out, "w", encoding="utf-8") as f:
        json.dump(relatorio, f, indent=2, ensure_ascii=False)
        
    print("\n" + "=" * 70)
    print(f" LAUDO PERICIAL GERADO EM: {caminho_out}")
    print("=" * 70)

if __name__ == "__main__":
    main()
