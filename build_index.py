#!/usr/bin/env python3
"""Gera docs/index.html — o índice de relatorios.fiquemsabendo.com.br.

Varre as pastas de primeiro nível que tenham um `relatorio.json` e uma página
publicada em `docs/<pasta>/index.html`, e monta um card para cada uma, do mais
recente para o mais antigo. Campos do JSON:

  titulo        obrigatório
  descricao     obrigatório
  tag           rótulo curto no chip amarelo (ex.: "Dados abertos")
  fonte         linha de fonte
  acao          texto do link (padrão: "Abrir")
  publicado_em  AAAA-MM-DD, usado na ordenação e exibido no card
  oculto        true para não listar

Enquanto houver um único relatório publicado, o índice é uma página de
redirecionamento para ele; a lista com cards só aparece a partir do segundo.

Roda localmente (`python3 build_index.py`) e no GitHub Actions a cada push.
"""
import base64
import html
import json
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.join(ROOT, "docs")
ASSETS = os.path.join(ROOT, "_identidade")   # fontes e logos da Fiquem Sabendo


def esc(s):
    return html.escape(str(s), quote=True)


def b64(path):
    return base64.b64encode(open(path, "rb").read()).decode("ascii")


def data_br(iso):
    try:
        a, m, d = iso.split("-")
        return f"{d}/{m}/{a}"
    except Exception:
        return iso or ""


relatorios = []
for nome in sorted(os.listdir(ROOT)):
    meta_path = os.path.join(ROOT, nome, "relatorio.json")
    pagina = os.path.join(DOCS, nome, "index.html")
    if not os.path.isfile(meta_path):
        continue
    meta = json.load(open(meta_path, encoding="utf-8"))
    if meta.get("oculto"):
        continue
    if not os.path.isfile(pagina):
        print(f"aviso: {nome}/relatorio.json existe mas docs/{nome}/index.html não — ignorado", file=sys.stderr)
        continue
    for k in ("titulo", "descricao"):
        if not meta.get(k):
            sys.exit(f"{nome}/relatorio.json sem o campo obrigatório '{k}'")
    meta["pasta"] = nome
    relatorios.append(meta)

relatorios.sort(key=lambda m: m.get("publicado_em", ""), reverse=True)

fonts = "\n".join(
    f"@font-face{{font-family:{fam};font-weight:{w};font-style:normal;font-display:swap;"
    f"src:url(data:font/woff2;base64,{b64(os.path.join(ASSETS, 'fonts', fn))}) format('woff2')}}"
    for fam, w, fn in [("Supply", 700, "Supply-Bold.woff2"), ("Roboto", 400, "Roboto-Regular.woff2"),
                       ("Roboto", 700, "Roboto-Bold.woff2")])
logo = (open(os.path.join(ASSETS, "logo.svg"), encoding="utf-8").read().strip()
        .replace('fill="#000"', 'fill="currentColor"')
        .replace("<svg ", '<svg role="img" aria-label="Fiquem Sabendo" ', 1))
logo_fs = (open(os.path.join(ASSETS, "logo-fs.svg"), encoding="utf-8").read().strip()
           .replace("<svg ", '<svg class="logo-fs" aria-hidden="true" ', 1))

cards = "\n".join(f'''    <a class="card" href="{esc(m["pasta"])}/">
      <span class="tag">{esc(m.get("tag", "Relatório"))}</span>
      <h2>{esc(m["titulo"])}</h2>
      <p>{esc(m["descricao"])}</p>
      <span class="meta">{esc(m.get("fonte", ""))}{(" · " if m.get("fonte") and m.get("publicado_em") else "")}{esc(data_br(m.get("publicado_em", "")))}</span><br>
      <span class="go">{esc(m.get("acao", "Abrir"))} →</span>
    </a>''' for m in relatorios) or '    <p class="vazio">Nenhum relatório publicado ainda.</p>'

n = len(relatorios)
page = f'''<meta charset="utf-8">
<title>Relatórios · Fiquem Sabendo</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="Relatórios e ferramentas de dados da Fiquem Sabendo.">
<link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 51 26'%3E%3Crect width='51' height='26' fill='%23000'/%3E%3Cpath fill='%23ffe706' d='M12.12 0H.433v25.998h11.685z'/%3E%3Cpath fill='%23fff' d='M16.695.387h13.689V3.57H21.63v7.412h8.302v3.19H21.63v11.832h-4.924zM39.388 17.97v1.719c0 1.634.582 2.392 2.148 2.392s1.952-1.123 1.952-2.296c0-2.345-.633-3.023-4.277-5.154-4.027-2.362-6.084-3.773-6.084-7.432 0-3.548 1.687-6.812 8.445-6.812 7.179 0 8.237 3.408 8.237 6.251v1.43h-6.49V6.58c0-1.503-.355-2.253-1.711-2.253-1.266 0-1.676.76-1.676 2.167 0 1.504.392 2.234 3.34 3.838 5.26 2.869 7.142 4.486 7.142 8.566 0 3.892-1.91 7.087-8.998 7.087-6.808 0-8.75-2.858-8.75-6.541V17.97z'/%3E%3C/svg%3E">
<!-- gerado por build_index.py a partir de <pasta>/relatorio.json — não edite à mão -->
<style>
{fonts}
:root {{ color-scheme: light; --ink:#000; --ink-2:#292929; --muted:#707070; --line:#ddd; --surface:#fff; --accent:#ffe706; --purple:#8103e5; --link:#1022ff; }}
* {{ box-sizing: border-box; }}
body {{ margin:0; background:var(--surface); color:var(--ink); font-family: Roboto, "Helvetica Neue", Arial, sans-serif; font-size:16px; line-height:1.5; -webkit-font-smoothing:antialiased; }}
a {{ color: var(--link); }}
.wrap {{ max-width: 1000px; margin: 0 auto; padding: 0 20px; }}
header {{ padding: 26px 0 8px; }}
.logo {{ display:block; width:148px; height:49px; color:var(--ink); }}
.logo svg {{ width:100%; height:100%; display:block; }}
h1 {{ font-family: Supply, "Roboto Mono", ui-monospace, monospace; font-size: clamp(28px, 4vw, 44px); line-height:1.25; margin: 34px 0 10px; max-width: 22ch; }}
mark {{ background: var(--accent); color:#000; padding:0 .12em; box-decoration-break: clone; -webkit-box-decoration-break: clone; }}
.dek {{ color: var(--ink-2); font-size: 17px; max-width: 62ch; margin: 0 0 12px; }}
.conta {{ font-size: 13px; color: var(--muted); margin: 0 0 28px; }}
.lista {{ display:grid; grid-template-columns: repeat(auto-fit, minmax(min(300px, 100%), 1fr)); gap:18px; margin: 0 0 60px; }}
.card {{ display:block; border:1px solid var(--line); border-radius:12px; padding:22px 24px 24px; color:inherit; text-decoration:none; }}
.card:hover {{ border-color: var(--ink); }}
.card .tag {{ display:inline-block; background:var(--accent); color:#000; font-size:12.5px; font-weight:700; padding:3px 9px; margin-bottom:12px; }}
.card h2 {{ font-family: Supply, ui-monospace, monospace; font-size: 22px; line-height:1.3; margin:0 0 8px; }}
.card p {{ color: var(--ink-2); font-size:15px; margin:0 0 12px; }}
.card .meta {{ font-size: 12.5px; color: var(--muted); }}
.card .go {{ display:inline-block; margin-top:14px; font-weight:700; color:var(--ink); border-bottom: 3px solid var(--accent); }}
.vazio {{ color: var(--muted); }}
footer {{ background:#000; color:#fff; padding: 40px 0 34px; }}
footer .fsrow {{ display:flex; align-items:center; gap:16px; flex-wrap:wrap; }}
footer .logo-fs {{ width:50px; height:auto; display:block; }}
footer p {{ margin:0; font-size:13.5px; max-width:72ch; }}
footer .fim {{ border-top:1px solid rgba(255,255,255,.18); margin-top:26px; padding-top:16px; font-size:12.5px; color:#a3a3a3; display:flex; justify-content:space-between; gap:12px; flex-wrap:wrap; }}
footer a {{ color: var(--accent); }}
</style>
<header class="wrap">
  <a class="logo" href="https://fiquemsabendo.com.br" target="_blank" rel="noopener">{logo}</a>
  <h1>Relatórios e <mark>ferramentas de dados</mark></h1>
  <p class="dek">Levantamentos feitos a partir de bases públicas, com pipeline aberto e reprodutível. Cada relatório tem sua própria página, fonte e metodologia.</p>
  <p class="conta">{n} relatório{"s" if n != 1 else ""} publicado{"s" if n != 1 else ""}</p>
</header>
<main class="wrap">
  <div class="lista">
{cards}
  </div>
</main>
<footer><div class="wrap">
  <div class="fsrow">{logo_fs}<p>A Fiquem Sabendo é uma organização sem fins lucrativos, independente e apartidária, cuja missão é reduzir o desequilíbrio de poder entre sociedade e Estado a partir do acesso a informações públicas.</p></div>
  <div class="fim"><span>Código: <a href="https://github.com/FiquemSabendo/relatorios" target="_blank" rel="noopener">github.com/FiquemSabendo/relatorios</a></span><span><a href="https://fiquemsabendo.com.br" target="_blank" rel="noopener">fiquemsabendo.com.br</a> · <a href="https://fiquemsabendo.com.br/contato" target="_blank" rel="noopener">Contato</a></span></div>
</div></footer>
'''
if n == 1:
    destino = relatorios[0]["pasta"] + "/"
    page = f'''<meta charset="utf-8">
<title>{esc(relatorios[0]["titulo"])} · Fiquem Sabendo</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="refresh" content="0; url={esc(destino)}">
<link rel="canonical" href="https://relatorios.fiquemsabendo.com.br/{esc(destino)}">
<!-- gerado por build_index.py: com um único relatório publicado, o índice redireciona para ele -->
<script>location.replace("{esc(destino)}" + location.hash);</script>
<p style="font-family:Roboto,Arial,sans-serif;padding:24px">Redirecionando para <a href="{esc(destino)}">{esc(relatorios[0]["titulo"])}</a>…</p>
'''

out = os.path.join(DOCS, "index.html")
open(out, "w", encoding="utf-8").write(page)
print(f"{out}: {n} relatório(s) — " + ", ".join(m["pasta"] for m in relatorios) + (" (redirecionamento)" if n == 1 else ""))
