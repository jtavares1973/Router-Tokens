# -*- coding: utf-8 -*-
"""
Auditoria Pericial de Qualidade e Regressão Silenciosa (Paridade contra Gabarito Padrão-Ouro do Argon)
Compara campo a campo, número a número e registro a registro o resultado gerado pelos modelos
do Router-Tokens contra o Gabarito Oficial do Argon em 3 tarefas analíticas reais do Scraper-OINA.
"""

import ast
import hashlib
import json
import sys
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

CAMINHO_SCRAPER_OINA = Path(r"D:\___SCRIPT\Scraper-OINA")
if str(CAMINHO_SCRAPER_OINA) not in sys.path:
    sys.path.insert(0, str(CAMINHO_SCRAPER_OINA))

from services.scraper_service import ScraperService
from router_tokens import DIRETORIO_LOGS, chamar_ollama, extrair_bloco_python


# =====================================================================================
# 1. PRÉ-CARREGAMENTO DOS DADOS REAIS DO OINA (UNIDADE ACL) PARA COMPARAÇÃO JUSTA
# =====================================================================================
servico_oina = ScraperService()
DF_TURMAS_ACL = servico_oina.get_turmas("ACL")
DF_ALUNOS_N1_ACL = servico_oina.get_alunos_n1("ACL")
DF_ESCALA_ACL = servico_oina.get_escala_professores("ACL")
DF_MEMBROS_N2_ACL = servico_oina.get_membros_n2("ACL", enriquecer_contatos=False)


# =====================================================================================
# 2. GABARITO PADRÃO-OURO DO ARGON (REFERÊNCIA 100% EXATA)
# =====================================================================================
def gabarito_argon_tarefa_1(df_turmas) -> Dict[str, Any]:
    """
    Tarefa 1 (Auditoria de Turmas por Dia da Semana):
    Contar quantas turmas existem em cada dia da semana, ordenar os dias alfabeticamente,
    identificar o dia com mais turmas e listar as salas únicas sem vazios ou '-'.
    """
    contagem_dias = df_turmas["Dia"].value_counts().to_dict()
    contagem_ordenada = {str(k).strip().upper(): int(v) for k, v in sorted(contagem_dias.items())}
    dia_maior = max(contagem_ordenada.items(), key=lambda x: x[1])[0] if contagem_ordenada else ""
    salas = sorted(
        {
            str(s).strip().upper()
            for s in df_turmas["Sala"].dropna().tolist()
            if str(s).strip() and str(s).strip() != "-"
        }
    )
    return {
        "total_turmas": int(len(df_turmas)),
        "turmas_por_dia": contagem_ordenada,
        "dia_com_mais_turmas": dia_maior,
        "salas_unicas_validas": salas,
    }


def gabarito_argon_tarefa_2(df_alunos_n1) -> Dict[str, Any]:
    """
    Tarefa 2 (Auditoria de Alunos N1 por Turma e Ano de Ingresso):
    Contar total de alunos N1, distribuir contagem por Turma, extrair o ano de 'Ingresso'
    (formato DD/MM/AAAA -> últimos 4 dígitos) contando quantos ingressaram em 2025 e 2026,
    e verificar se há matrículas duplicadas.
    """
    por_turma = {str(k).strip(): int(v) for k, v in sorted(df_alunos_n1["Turma"].value_counts().to_dict().items())}
    ingressos = df_alunos_n1["Ingresso"].astype(str).str.strip()
    anos = ingressos.apply(lambda x: x.split("/")[-1] if "/" in x and len(x.split("/")[-1]) == 4 else "OUTRO")
    contagem_anos = anos.value_counts().to_dict()
    matriculas_duplicadas = int(df_alunos_n1["Matricula"].duplicated().sum())
    return {
        "total_alunos_n1": int(len(df_alunos_n1)),
        "alunos_por_turma": por_turma,
        "ingressos_2025": int(contagem_anos.get("2025", 0)),
        "ingressos_2026": int(contagem_anos.get("2026", 0)),
        "matriculas_duplicadas": matriculas_duplicadas,
    }


def gabarito_argon_tarefa_3(df_escala, df_membros_n2) -> Dict[str, Any]:
    """
    Tarefa 3 (Cruzamento Relacional Docente x Membros N2):
    Extrair professores únicos na escala (coluna 'Professor' limpa em maiúsculas),
    calcular a média de alocações por professor único (arredondada em 2 casas),
    e cruzar quantos desses professores únicos constam na coluna 'Nome_Norm' (ou 'Nome') de df_membros_n2.
    """
    col_prof = "Professor" if "Professor" in df_escala.columns else df_escala.columns[2]
    profs_escala = {
        str(p).strip().upper()
        for p in df_escala[col_prof].dropna().tolist()
        if str(p).strip() and str(p).strip() != "-"
    }
    col_nome_membro = "Nome_Norm" if "Nome_Norm" in df_membros_n2.columns else "Nome"
    nomes_membros = {
        str(n).strip().upper()
        for n in df_membros_n2[col_nome_membro].dropna().tolist()
        if str(n).strip()
    }
    profs_encontrados_n2 = sorted(profs_escala.intersection(nomes_membros))
    qtd_profs = len(profs_escala)
    media_aloc = round(len(df_escala) / qtd_profs, 2) if qtd_profs > 0 else 0.0
    return {
        "total_alocacoes_escala": int(len(df_escala)),
        "total_professores_unicos": int(qtd_profs),
        "media_alocacoes_por_professor": float(media_aloc),
        "professores_confirmados_em_n2": int(len(profs_encontrados_n2)),
    }


# =====================================================================================
# 3. MOTOR DE CÁLCULO DE QUALIDADE E REGRESSÃO SILENCIOSA (0% A 100%)
# =====================================================================================
def comparar_contra_gabarito(gabarito: Dict[str, Any], resposta_modelo: Any) -> Dict[str, Any]:
    """
    Compara chave por chave e valor por valor a saída do modelo contra o Gabarito Padrão-Ouro do Argon.
    Retorna nota de 0.0 a 100.0, lista de divergências exatas e flag de regressão silenciosa.
    """
    if not isinstance(resposta_modelo, dict):
        return {
            "nota_qualidade": 0.0,
            "chaves_corretas": 0,
            "total_chaves": len(gabarito),
            "regressao_silenciosa": True,
            "divergencias": [f"Retorno não é dicionário: {type(resposta_modelo).__name__}"],
        }

    total_chaves = len(gabarito)
    pontos = 0.0
    divergencias = []

    for chave, valor_esperado in gabarito.items():
        if chave not in resposta_modelo:
            divergencias.append(f"Chave ausente: '{chave}' (esperado: {valor_esperado})")
            continue

        valor_obtido = resposta_modelo[chave]
        if valor_obtido == valor_esperado:
            pontos += 1.0
        elif isinstance(valor_esperado, float) and isinstance(valor_obtido, (int, float)):
            if abs(float(valor_obtido) - valor_esperado) <= 0.01:
                pontos += 1.0
            else:
                divergencias.append(f"Diferença numérica em '{chave}': esperado={valor_esperado}, obtido={valor_obtido}")
        elif isinstance(valor_esperado, dict) and isinstance(valor_obtido, dict):
            # Compara subchaves normalizando maiúsculas
            norm_esp = {str(k).strip().upper(): v for k, v in valor_esperado.items()}
            norm_obt = {str(k).strip().upper(): v for k, v in valor_obtido.items()}
            if norm_esp == norm_obt:
                pontos += 1.0
            else:
                acertos_sub = sum(1 for k, v in norm_esp.items() if norm_obt.get(k) == v)
                parcial = acertos_sub / max(1, len(norm_esp))
                pontos += parcial
                divergencias.append(f"Divergência parcial em '{chave}': esperado={norm_esp}, obtido={norm_obt}")
        elif isinstance(valor_esperado, list) and isinstance(valor_obtido, list):
            norm_esp_l = sorted(str(x).strip().upper() for x in valor_esperado)
            norm_obt_l = sorted(str(x).strip().upper() for x in valor_obtido)
            if norm_esp_l == norm_obt_l:
                pontos += 1.0
            else:
                divergencias.append(f"Lista divergente em '{chave}': esperado={norm_esp_l}, obtido={norm_obt_l}")
        else:
            if str(valor_obtido).strip().upper() == str(valor_esperado).strip().upper():
                pontos += 1.0
            else:
                divergencias.append(f"Valor divergente em '{chave}': esperado={valor_esperado}, obtido={valor_obtido}")

    nota = round((pontos / total_chaves) * 100.0, 1)
    # Regressão silenciosa = o código compilou e rodou sem exceção, mas entregou resultado diferente do Argon (< 100%)
    regressao_silenciosa = nota < 100.0
    return {
        "nota_qualidade": nota,
        "chaves_corretas": round(pontos, 2),
        "total_chaves": total_chaves,
        "regressao_silenciosa": regressao_silenciosa,
        "divergencias": divergencias,
    }


def avaliar_modelo_na_tarefa(
    modelo: str,
    nome_tarefa: str,
    prompt_tarefa: str,
    argumentos_execucao: Tuple[Any, ...],
    gabarito_esperado: Dict[str, Any],
) -> Dict[str, Any]:
    """Executa a geração da função no modelo, roda sobre os DataFrames reais e mede a paridade contra o Argon."""
    t0 = time.perf_counter()
    ok, resposta_bruta, tok_in, tok_out = chamar_ollama(
        instrucao=prompt_tarefa,
        modelo=modelo,
        temperatura=0.0,
        timeout_seg=90,
    )
    tempo_ms = int((time.perf_counter() - t0) * 1000)
    codigo = extrair_bloco_python(resposta_bruta)

    if not ok or not codigo:
        return {
            "modelo": modelo,
            "tarefa": nome_tarefa,
            "compilou": False,
            "executou": False,
            "nota_qualidade": 0.0,
            "regressao_silenciosa": False,
            "tempo_ms": tempo_ms,
            "divergencias": ["Não gerou bloco de código Python válido."],
        }

    try:
        ast.parse(codigo)
    except SyntaxError as e:
        return {
            "modelo": modelo,
            "tarefa": nome_tarefa,
            "compilou": False,
            "executou": False,
            "nota_qualidade": 0.0,
            "regressao_silenciosa": False,
            "tempo_ms": tempo_ms,
            "divergencias": [f"Erro de Sintaxe (Pego no Portão A): {e}"],
        }

    escopo: Dict[str, Any] = {}
    try:
        exec(compile(codigo, "<auditoria_qualidade>", "exec"), escopo)
        func = escopo.get("resolver_tarefa")
        if not callable(func):
            raise RuntimeError("Função `resolver_tarefa` não encontrada.")
        saida_modelo = func(*argumentos_execucao)
    except Exception as e:
        return {
            "modelo": modelo,
            "tarefa": nome_tarefa,
            "compilou": True,
            "executou": False,
            "nota_qualidade": 0.0,
            "regressao_silenciosa": False,
            "tempo_ms": tempo_ms,
            "divergencias": [f"Erro em Tempo de Execução (Pego no Portão A): {type(e).__name__}: {e}"],
        }

    avaliacao = comparar_contra_gabarito(gabarito_esperado, saida_modelo)
    return {
        "modelo": modelo,
        "tarefa": nome_tarefa,
        "compilou": True,
        "executou": True,
        "nota_qualidade": avaliacao["nota_qualidade"],
        "regressao_silenciosa": avaliacao["regressao_silenciosa"],
        "tempo_ms": tempo_ms,
        "tokens_in": tok_in,
        "tokens_out": tok_out,
        "divergencias": avaliacao["divergencias"],
        "saida_modelo": saida_modelo,
    }


if __name__ == "__main__":
    print("=" * 95)
    print(" AUDITORIA DE QUALIDADE E REGRESSÃO SILENCIOSA: MODELOS ROUTER vs. GABARITO PADRÃO-OURO ARGON")
    print("=" * 95)

    gab1 = gabarito_argon_tarefa_1(DF_TURMAS_ACL)
    gab2 = gabarito_argon_tarefa_2(DF_ALUNOS_N1_ACL)
    gab3 = gabarito_argon_tarefa_3(DF_ESCALA_ACL, DF_MEMBROS_N2_ACL)

    print("\n[GABARITO OFICIAL ARGON - 100% REFERÊNCIA]")
    print(f" -> Tarefa 1 (Turmas por Dia e Salas Limpas): {json.dumps(gab1, ensure_ascii=False)}")
    print(f" -> Tarefa 2 (Alunos N1 por Turma, Anos 2025/2026 e Duplicatas): {json.dumps(gab2, ensure_ascii=False)}")
    print(f" -> Tarefa 3 (Cruzamento Relacional Professores x Membros N2): {json.dumps(gab3, ensure_ascii=False)}")

    prompt_t1 = (
        "Não use pensamento longo. Escreva apenas um bloco ```python``` com `def resolver_tarefa(df_turmas):` que receba um DataFrame pandas "
        "com as colunas `['Unidade', 'Nivel', 'Turma', 'Dia', 'Horario', 'Inicio', 'Conclusao_Prevista', 'Sala', 'Tipo']` e retorne um dict com:\n"
        "- `'total_turmas'`: int com total de linhas;\n"
        "- `'turmas_por_dia'`: dict mapeando cada `Dia` (em maiúsculas e `.strip()`) para sua contagem `int`, ordenado pelas chaves;\n"
        "- `'dia_com_mais_turmas'`: string do dia que possui a maior quantidade de turmas;\n"
        "- `'salas_unicas_validas'`: lista ordenada de strings únicas da coluna `Sala` (em maiúsculas e `.strip()`), ignorando vazios e `'-'`."
    )

    prompt_t2 = (
        "Não use pensamento longo. Escreva apenas um bloco ```python``` com `def resolver_tarefa(df_alunos_n1):` que receba um DataFrame pandas "
        "com as colunas `['Unidade', 'Matricula', 'Nome', 'Nome_Norm', 'Turma', 'Ingresso']` (onde `Ingresso` está no formato `'DD/MM/AAAA'`) e retorne um dict com:\n"
        "- `'total_alunos_n1'`: int com total de linhas;\n"
        "- `'alunos_por_turma'`: dict mapeando cada `Turma` (`.strip()`) para sua contagem `int`;\n"
        "- `'ingressos_2025'`: int contando quantos alunos têm ano de ingresso igual a `'2025'` (últimos 4 dígitos após `'/'`);\n"
        "- `'ingressos_2026'`: int contando quantos alunos têm ano de ingresso igual a `'2026'`;\n"
        "- `'matriculas_duplicadas'`: int com `int(df_alunos_n1['Matricula'].duplicated().sum())`."
    )

    prompt_t3 = (
        "Não use pensamento longo. Escreva apenas um bloco ```python``` com `def resolver_tarefa(df_escala, df_membros_n2):` que receba dois DataFrames pandas:\n"
        "`df_escala` (com coluna `'Professor'`) e `df_membros_n2` (com coluna `'Nome_Norm'`).\n"
        "Extraia o conjunto de nomes únicos de `df_escala['Professor']` (limpos com `.strip().upper()`, ignorando vazios e `'-'`).\n"
        "Extraia o conjunto de nomes únicos de `df_membros_n2['Nome_Norm']` (limpos com `.strip().upper()`, ignorando vazios).\n"
        "Retorne um dict com:\n"
        "- `'total_alocacoes_escala'`: int com `len(df_escala)`;\n"
        "- `'total_professores_unicos'`: int com a quantidade de professores únicos na escala;\n"
        "- `'media_alocacoes_por_professor'`: float com `round(len(df_escala) / total_professores_unicos, 2)`;\n"
        "- `'professores_confirmados_em_n2'`: int com a quantidade de professores únicos da escala que aparecem exatamente no conjunto `'Nome_Norm'` de `df_membros_n2`."
    )

    modelos_para_testar = [
        "qwen2.5-coder:7b",
        "qwen3.8-32k:latest",
        "deepseek-v4.1-flash:cloud",
    ]

    resultados_gerais = []
    for mod in modelos_para_testar:
        print(f"\n{'-' * 95}")
        print(f" AUDITANDO MODELO: {mod} CONTRA O GABARITO DO ARGON...")
        print(f"{'-' * 95}")
        r_t1 = avaliar_modelo_na_tarefa(mod, "T1_Turmas_Salas", prompt_t1, (DF_TURMAS_ACL,), gab1)
        r_t2 = avaliar_modelo_na_tarefa(mod, "T2_Alunos_N1_Ingressos", prompt_t2, (DF_ALUNOS_N1_ACL,), gab2)
        r_t3 = avaliar_modelo_na_tarefa(mod, "T3_Cruzamento_Docentes_N2", prompt_t3, (DF_ESCALA_ACL, DF_MEMBROS_N2_ACL), gab3)

        for r in (r_t1, r_t2, r_t3):
            resultados_gerais.append(r)
            status_reg = "ALERTA REGRESSÃO SILENCIOSA!" if r["regressao_silenciosa"] else "ZERO REGRESSÃO (100% FIEL AO ARGON)"
            print(
                f" -> [{r['tarefa']}] Nota de Qualidade: {r['nota_qualidade']}% | "
                f"Tempo: {r['tempo_ms']} ms | Status: {status_reg}"
            )
            if r["divergencias"]:
                for div in r["divergencias"]:
                    print(f"    * Divergência detectada: {div}")

    DIRETORIO_LOGS.mkdir(parents=True, exist_ok=True)
    arquivo_paridade = DIRETORIO_LOGS / "auditoria_qualidade_paridade_argon.json"
    with open(arquivo_paridade, "w", encoding="utf-8") as f:
        json.dump(
            {
                "gabarito_argon": {"T1": gab1, "T2": gab2, "T3": gab3},
                "avaliacoes": resultados_gerais,
            },
            f,
            indent=2,
            ensure_ascii=False,
        )
    print(f"\n{'=' * 95}")
    print(f" LAUDO DE QUALIDADE E PARIDADE SALVO EM: {arquivo_paridade}")
    print(f"{'=' * 95}")
