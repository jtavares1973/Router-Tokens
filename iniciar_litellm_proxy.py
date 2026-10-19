# -*- coding: utf-8 -*-
"""
Inicializador Oficial do LiteLLM Proxy — Estação ZAMORA (Porta 4000)
Força UTF-8 no ambiente Windows para evitar falha no banner ANSI.
"""

import os
import sys
import subprocess
from pathlib import Path

# Força codificação UTF-8 padrão em todas as chamadas Python filhas
os.environ["PYTHONIOENCODING"] = "utf-8"
os.environ["PYTHONUTF8"] = "1"

def main():
    diretorio = Path(__file__).resolve().parent
    arquivo_config = diretorio / "litellm_config.yaml"
    
    if not arquivo_config.exists():
        print(f"Erro: Arquivo de configuracao nao encontrado em {arquivo_config}")
        sys.exit(1)
        
    print("=================================================================")
    print(" INICIANDO LITELLM PROXY - ESTACAO ZAMORA (POLITICA 90/10)")
    print(f" Configuracao: {arquivo_config}")
    print(" Porta: 4000 (127.0.0.1)")
    print("=================================================================")
    
    comando = [
        sys.executable,
        "-m", "litellm.proxy.proxy_cli",
        "--config", str(arquivo_config),
        "--port", "4000",
        "--host", "127.0.0.1"
    ]
    
    try:
        subprocess.run(comando, check=True)
    except KeyboardInterrupt:
        print("\nLiteLLM Proxy encerrado pelo usuario.")
    except Exception as e:
        print(f"Erro na execucao do LiteLLM Proxy: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
