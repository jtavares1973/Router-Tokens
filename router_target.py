# -*- coding: utf-8 -*-
"""
Wrapper Oficial do Roteador para o Framework Promptfoo — Estação ZAMORA
Retorna JSON estruturado no output para auditoria transparente de asserções.
"""

import json
import time
from typing import Dict, Any

from router_tokens import executar_roteamento

def call_api(prompt: str, options: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
    prompt_str = str(prompt or "")
    
    vars_ctx = (context or {}).get("vars", {})
    qtd_arquivos = int(vars_ctx.get("arquivos", 1))
    
    t0 = time.perf_counter()
    resultado = executar_roteamento(
        instrucao=prompt_str,
        arquivos_envolvidos=qtd_arquivos
    )
    tempo_total_ms = int((time.perf_counter() - t0) * 1000)
    
    if "DEGRAU_1" in resultado.camada_acionada:
        backend_tag = "local_gpu"
    elif "DEGRAU_2" in resultado.camada_acionada:
        backend_tag = "agentic_deepseek"
    elif "DEGRAU_3" in resultado.camada_acionada:
        backend_tag = "antigravity_fast"
    else:
        backend_tag = "antigravity_cloud"
        
    dados_resposta = {
        "resposta": resultado.resposta,
        "routed_to": backend_tag,
        "camada_oficial": resultado.camada_acionada,
        "modelo_utilizado": resultado.modelo_utilizado,
        "motor_utilizado": resultado.motor_utilizado,
        "sucesso": resultado.sucesso,
        "validacao_deterministica": resultado.validacao_deterministica,
        "tempo_ms": resultado.tempo_ms or tempo_total_ms,
        "tokens_entrada": resultado.tokens_entrada,
        "tokens_saida": resultado.tokens_saida,
        "custo_usd": resultado.custo_estimado_usd,
        "economizou_nuvem": backend_tag in ("local_gpu", "agentic_deepseek")
    }
    
    return {
        "output": json.dumps(dados_resposta, ensure_ascii=False),
        "metadata": dados_resposta
    }

if __name__ == "__main__":
    res = call_api("Escreva def somar(a, b): return a + b")
    print(res["output"])
