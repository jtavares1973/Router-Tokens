# -*- coding: utf-8 -*-
"""
Teste de Integração Oficial do LiteLLM Proxy — Estação ZAMORA
Valida o executor principal local Qwen 2.5 Coder 32B na RTX 5090.
"""

import json
import time
import urllib.request

URL_LITELLM = "http://127.0.0.1:4000/v1/chat/completions"
API_KEY = "sk-zamora-pericial-5090"

def testar_executor_32b():
    print("Testando chamada ao modelo principal zamora-executor-local (32B) na RTX 5090...")
    carga = {
        "model": "zamora-executor-local",
        "messages": [
            {
                "role": "user",
                "content": "Escreva uma funcao Python def somar(a, b): return a + b com docstring completa em Portugues."
            }
        ],
        "temperature": 0.1,
        "max_tokens": 150
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
        modelo_resposta = corpo.get("model", "")
        uso = corpo.get("usage", {})
        
        print("\n=======================================================")
        print(" RESPOSTA DO EXECUTOR 32B NA RTX 5090 (SUCESSO TOTAL)")
        print(f" Modelo Retornado: {modelo_resposta}")
        print(f" Tempo de Resposta: {tempo_ms} ms")
        print(f" Tokens Entrada: {uso.get('prompt_tokens', 0)}")
        print(f" Tokens Saida: {uso.get('completion_tokens', 0)}")
        print(f" Conteudo:\n{texto.strip()}")
        print("=======================================================")

if __name__ == "__main__":
    testar_executor_32b()
