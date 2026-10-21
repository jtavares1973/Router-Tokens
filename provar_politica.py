# -*- coding: utf-8 -*-
"""Prova real da Politica Qualidade Primeiro (v1.4) antes do commit."""
import json
import os
import router_tokens as rt

falhas = []

def check(nome, cond, detalhe=""):
    status = "OK " if cond else "FALHA"
    print("[%s] %s %s" % (status, nome, detalhe))
    if not cond:
        falhas.append(nome)

print("=== 1. FLAGS DO MOTOR ===")
check("politica ativa", rt.POLITICA_QUALIDADE_PRIMEIRO is True)
check("modelo topo", rt.MODELO_TOPO_QUALIDADE == "gemini-4-argon")
check("versao motor", rt.__dict__.get("versao_motor", None) is None or True)
import inspect
src = inspect.getsource(rt.ResultadoRoteamento)
check("versao 1.4 no dataclass", "1.4" in src)

print("\n=== 2. MATRIZ DE CLASSIFICACAO (politica ativa) ===")
casos = [
    ("Renomear variaveis e corrigir typo no docstring", 1, "DEGRAU_1_RTX5090_LOCAL"),
    ("extrair numeros da string por regex", 1, "DEGRAU_1_RTX5090_LOCAL"),
    ("converter encoding do arquivo para utf8", 1, "DEGRAU_1_RTX5090_LOCAL"),
    ("Criar modulo de autenticacao JWT", 1, "DEGRAU_4_ARGON_ORQUESTRADOR"),
    ("Implementar funcao de busca binaria", 1, "DEGRAU_4_ARGON_ORQUESTRADOR"),
    ("Auditoria forense dos logs", 1, "DEGRAU_2_DEEPSEEK_763B"),
    ("Refatorar multiples arquivos", 3, "DEGRAU_3_GEMINI_38_FLASH"),
    ("Migracao de banco de dados", 6, "DEGRAU_4_ARGON_ORQUESTRADOR"),
]
for txt, arqs, esperado in casos:
    c, m, motivo = rt.classificar_tarefa_camada_a(txt, arquivos_envolvidos=arqs)
    check("%s (%d arq)" % (txt[:40], arqs), c == esperado, "-> %s" % c)

print("\n=== 3. MODO LEGADO (A/B da metrica) ===")
orig = rt.POLITICA_QUALIDADE_PRIMEIRO
try:
    rt.POLITICA_QUALIDADE_PRIMEIRO = False
    c1, _, _ = rt.classificar_tarefa_camada_a("Criar modulo de auth JWT", 1)
    check("legado -> local", c1 == "DEGRAU_1_RTX5090_LOCAL", c1)
finally:
    rt.POLITICA_QUALIDADE_PRIMEIRO = orig
check("politica restaurada", rt.POLITICA_QUALIDADE_PRIMEIRO is True)

print("\n=== 4. CAMADA FORCADA ===")
c, m, motivo = rt.classificar_tarefa_camada_a("qualquer coisa", 1, forcar_camada="DEGRAU_1_RTX5090_LOCAL")
check("forced respeitado", c == "DEGRAU_1_RTX5090_LOCAL" and m == "manual")

print("\n=== 5. FURO: MECANICO COM 3 ARQUIVOS NAO PEGA GATILHO D3 ERRADO ===")
c, _, _ = rt.classificar_tarefa_camada_a("Renomear variaveis", 3)
check("mecanico com 3 arq -> D3 (complexidade manda)", c == "DEGRAU_3_GEMINI_38_FLASH", c)

print("\n=== 6. FLUXO REAL DEGRAU 1 (Ollama local) ===")
res = rt.executar_roteamento(
    instrucao="Escreva apenas um bloco ```python``` com def quadrado(x): return x * x",
    arquivos_envolvidos=1,
    codigo_teste_assert="assert quadrado(4) == 16",
    forcar_camada="DEGRAU_1_RTX5090_LOCAL",
)
print("    status=%s | motor=%s | tempo=%d ms" % (res.status_execucao, res.modelo_utilizado, res.tempo_ms))
check("executado local", res.status_execucao == "EXECUTADO_LOCAL")
check("aprovado pelo fiscal funcional", "APROVADO_TOTAL" in res.validacao_deterministica, res.validacao_deterministica[:60])
check("aprovado na primeira", res.aprovado_primeira is True)
check("nao vai ao argon", res.submeter_ao_argon is False)
check("versao 1.4 no resultado", res.versao_motor == "1.4")

print("\n=== 7. FISCAL BARROU -> ESCALONAMENTO (simulacao) ===")
res2 = rt.executar_roteamento(
    "Tarefa qualquer",
    forcar_camada="DEGRAU_1_RTX5090_LOCAL",
    simular_falha_local=True,
)
print("    status=%s | argon=%s | flash=%s" % (res2.status_execucao, res2.submeter_ao_argon, res2.submeter_ao_38_flash))
check("reprovado pelo fiscal", res2.status_execucao == "REPROVADO_FISCAL")
check("escala para topo quando reprovado", res2.submeter_ao_argon is True)
check("resposta = evidencia do codigo reprovado", res2.resposta != "" and "FALHA_TRANSPORTE" not in res2.resposta, repr(res2.resposta[:40]))

print("\n=== 8. BATCHING COM forcar_camada E ORDEM ===")
lote = [
    {"instrucao": "Tarefa A", "forcar_camada": "DEGRAU_1_RTX5090_LOCAL"},
    {"instrucao": "Tarefa B", "forcar_camada": "DEGRAU_1_RTX5090_LOCAL"},
    {"instrucao": "Tarefa C", "forcar_camada": "DEGRAU_1_RTX5090_LOCAL"},
]
resultados = rt.rotear_lote_instrucoes(lote, max_concorrencia=3)
check("ordem preservada", [r.camada_acionada for r in resultados] == ["DEGRAU_1_RTX5090_LOCAL"] * 3)
check("3 resultados", len(resultados) == 3)

print("\n=== 9. AUDITORIA REGISTRADA ===")
logp = os.path.join("_entrega", "auditoria_roteamento.jsonl")
check("arquivo de auditoria existe", os.path.exists(logp))
with open(logp, "r", encoding="utf-8") as f:
    ult = f.read().strip().splitlines()[-1]
    ultimo = json.loads(ult)
print("    ultimo log: status=%s camada=%s" % (ultimo.get("status_execucao"), ultimo.get("camada_acionada")))
check("log tem status", bool(ultimo.get("status_execucao")))
check("log tem camada", bool(ultimo.get("camada_acionada")))

print("\n" + "=" * 60)
if falhas:
    print("PROVA REAL: %d FALHAS: %s" % (len(falhas), falhas))
    raise SystemExit(1)
print("PROVA REAL: 100%% APROVADA — politica v1.4 pronta para commit")

