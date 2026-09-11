#!/usr/bin/env python3
"""Costura relatorio/template.html + relatorio/base.css + relatorio/dados.json + fontes
e logos (artifact/assets) em docs/index.html — a página servida pelo GitHub Pages."""
import base64
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REL = os.path.join(ROOT, "relatorio")
ASSETS = os.path.join(ROOT, "artifact", "assets")
OUT = os.path.join(ROOT, "docs", "index.html")

FACES = [("Supply", 400, "Supply-Regular.woff2"), ("Supply", 700, "Supply-Bold.woff2"),
         ("Roboto", 400, "Roboto-Regular.woff2"), ("Roboto", 500, "Roboto-Medium.woff2"),
         ("Roboto", 700, "Roboto-Bold.woff2")]


def font_css():
    out = []
    for family, weight, fname in FACES:
        b64 = base64.b64encode(open(os.path.join(ASSETS, "fonts", fname), "rb").read()).decode("ascii")
        out.append(f"@font-face{{font-family:{family};font-weight:{weight};font-style:normal;"
                   f"font-display:swap;src:url(data:font/woff2;base64,{b64}) format('woff2')}}")
    return "\n".join(out)


def ler(*p):
    return open(os.path.join(*p), encoding="utf-8").read()


tpl = ler(REL, "template.html")
dados = ler(REL, "dados.json").replace("</", "<\\/").replace("<!--", "<\\u0021--")
logo = (ler(ASSETS, "logo.svg").strip().replace('fill="#000"', 'fill="currentColor"')
        .replace("<svg ", '<svg role="img" aria-label="Fiquem Sabendo" ', 1))
logo_fs = ler(ASSETS, "logo-fs.svg").strip().replace("<svg ", '<svg class="logo-fs" aria-hidden="true" ', 1)

for m in ("__FONTS__", "__BASE_CSS__", "__DADOS__", "__LOGO__", "__LOGO_FS__"):
    if m not in tpl:
        sys.exit(f"template sem marcador {m}")
html = (tpl.replace("__FONTS__", font_css()).replace("__BASE_CSS__", ler(REL, "base.css"))
        .replace("__LOGO__", logo).replace("__LOGO_FS__", logo_fs).replace("__DADOS__", dados))
os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, "w", encoding="utf-8").write(html)
print(f"{OUT}  {os.path.getsize(OUT)/1e3:.0f} KB")
