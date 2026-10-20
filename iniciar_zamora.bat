@echo off
chcp 65001 > nul
title ESTACAO ZAMORA - LITELLM PROXY (PORTA 4000)
color 0A

echo ==============================================================================
echo  INICIALIZADOR CANONICO - ESTACAO ZAMORA
echo  Politica 90/10 ^| NVIDIA GeForce RTX 5090 ^| LiteLLM Proxy Porta 4000
echo ==============================================================================
echo.

set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1

echo [*] Verificando servico do LiteLLM Proxy...
python "%~dp0iniciar_litellm_proxy.py"

pause
