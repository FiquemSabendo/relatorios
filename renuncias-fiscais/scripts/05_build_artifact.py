#!/usr/bin/env python3
"""Costura artifact/template.html + artifact/payload.json + fontes em um HTML autocontido.

Saídas (idênticas):
  artifact/renuncias.html   — nome histórico, usado para publicar o artefato no claude.ai
  ../docs/renuncias-fiscais/index.html — o que o GitHub Pages serve
"""
import base64
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TPL = os.path.join(ROOT, "artifact", "template.html")
PAY = os.path.join(ROOT, "artifact", "payload.json")
FONTS = os.path.join(ROOT, "artifact", "assets", "fonts")
OUTS = [os.path.join(ROOT, "artifact", "renuncias.html"),
        os.path.join(os.path.dirname(ROOT), "docs", "renuncias-fiscais", "index.html")]

# Identidade visual da Fiquem Sabendo: Supply (títulos) + Roboto (texto), as mesmas
# faces servidas em fiquemsabendo.com.br. Embutidas como data URI porque o site não
# manda cabeçalho CORS (fonte cross-origin é bloqueada) e porque o artefato do
# claude.ai não pode buscar nada fora da página.
FACES = [
    ("Supply", 400, "Supply-Regular.woff2"),
    ("Supply", 700, "Supply-Bold.woff2"),
    ("Roboto", 400, "Roboto-Regular.woff2"),
    ("Roboto", 500, "Roboto-Medium.woff2"),
    ("Roboto", 700, "Roboto-Bold.woff2"),
]


def font_css():
    out = []
    for family, weight, fname in FACES:
        path = os.path.join(FONTS, fname)
        if not os.path.exists(path):
            sys.exit(f"fonte ausente: {path}")
        b64 = base64.b64encode(open(path, "rb").read()).decode("ascii")
        out.append(
            f"@font-face{{font-family:{family};font-weight:{weight};font-style:normal;"
            f"font-display:swap;src:url(data:font/woff2;base64,{b64}) format('woff2')}}"
        )
    return "\n".join(out)


tpl = open(TPL, encoding="utf-8").read()
pay = open(PAY, encoding="utf-8").read()
apresentacao = open(os.path.join(ROOT, "artifact", "apresentacao.json"), encoding="utf-8").read()

# Impede publicar a configuração de cobertura com deflatores antigos.
coverage = json.load(open(os.path.join(ROOT, "data", "macro", "cobertura-deflacao.json"), encoding="utf-8"))["anos"]
for row in json.loads(apresentacao)["anos"]:
    if row.get("meses_origem") != coverage.get(str(row["ano"])) or not row.get("indice_origem"):
        sys.exit("Deflatores desatualizados: execute scripts/11_export_apresentacao.py")

# Dentro de <script type="application/json"> o navegador ainda procura por "</script>"
# e por "<!--". "\/" é escape válido de JSON, então neutralizar "</" mantém o JSON
# íntegro e impede o fechamento prematuro da tag.
pay = pay.replace("</", "<\\/").replace("<!--", "<\\u0021--")

for marker in ("__PAYLOAD__", "__FONTS__", "__APRESENTACAO__"):
    if marker not in tpl:
        sys.exit(f"template sem marcador {marker}")
html = tpl.replace("__FONTS__", font_css()).replace("__PAYLOAD__", pay).replace("__APRESENTACAO__", apresentacao.replace("</", "<\\/"))

for out in OUTS:
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w", encoding="utf-8").write(html)
    n = os.path.getsize(out)
    print(f"{out}  {n/1e6:.2f} MB  ({'ok' if n < 16e6 else 'ACIMA DO LIMITE DE 16 MB'})")
