# -*- coding: utf-8 -*-
import io

def load(p):
    with io.open(p, "r", encoding="latin-1", newline="") as f:
        s = f.read()
    eol = "\r\n" if "\r\n" in s else "\n"
    return s.replace("\r\n", "\n"), eol

def save(p, s, eol):
    if eol == "\r\n":
        s = s.replace("\n", "\r\n")
    with io.open(p, "w", encoding="latin-1", newline="") as f:
        f.write(s)

p = "router_tokens.py"
code, eol = load(p)

start_marker = "# 0. POLITICA DE QUALIDADE PRIMEIRO (v1.4)"
head = "# ============================================================================\n"
si = code.find(head + start_marker)
if si == -1:
    raise SystemExit("inicio nao achado")
end_marker = '"adicionar log", "print de debug"\n]\n\n\n'
ei = code.find(end_marker, si)
if ei == -1:
    raise SystemExit("fim nao achado")
ei += len(end_marker)
block = code[si:ei]
code = code[:si] + code[ei:]

anchor = "MODELOS_DISPONIVEIS = {"
if block in code:
    raise SystemExit("bloco duplicado?")
i = code.find(anchor)
if i == -1:
    raise SystemExit("MODELOS_DISPONIVEIS nao achado")
code = code[:i] + block + code[i:]
save(p, code, eol)
print("REPARO OK: bloco realocado antes de MODELOS_DISPONIVEIS")
