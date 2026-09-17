#!/usr/bin/env python3
"""Gera o payload embutido no artefato.

O artefato é HTML autocontido e a CSP bloqueia qualquer requisição externa, então
os microdados viajam dentro do próprio arquivo: TSV -> gzip -> base64, e o
navegador descomprime com DecompressionStream('gzip') (API nativa, sem lib).

Quatro blobs:
  DIM   uma linha por CNPJ, na ordem de estab_id (o índice da linha É o estab_id)
  FATO  uma linha por CNPJ: pares "ano_offset valor" a partir de 2015
  ITEM  uma linha por CNPJ: trincas "ano_offset item_id valor" — o grão mais fino
        que a origem oferece (benefício fiscal × fundamento legal), para TODOS os
        CNPJs, que é o que permite rastrear a origem jurídica de cada renúncia
  AGG   cubo exato ano × item × seção CNAE × UF, para que os cortes por setor e
        UF continuem exatos nos painéis agregados

As métricas de outlier NÃO são pré-calculadas aqui: o JS as recomputa a partir de
FATO no carregamento, o que deixa o limiar do slider realmente interativo.
"""
import base64
import datetime
import gzip
import io
import json
import os
import sys

import duckdb
from classificacao_setorial import classificar_estabelecimentos, VERSION

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, "renuncias.duckdb")
OUT = os.path.join(ROOT, "artifact", "payload.json")
ANO0 = 2015
ANO_PARCIAL = 2024


def blob(linhas):
    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode="wb", compresslevel=9, mtime=0) as gz:
        gz.write("\n".join(linhas).encode("utf-8"))
    return base64.b64encode(buf.getvalue()).decode("ascii"), buf.tell()


def main():
    con = duckdb.connect(DB, read_only=True)

    # -------------------------------------------------------- dims pequenas --
    muns = con.execute(
        "SELECT DISTINCT municipio, uf FROM dim_estab ORDER BY uf, municipio"
    ).fetchall()
    mun_id = {(m, u): i for i, (m, u) in enumerate(muns)}

    cnaes = con.execute(
        "SELECT cnae, descricao, secao, secao_nome FROM dim_cnae ORDER BY cnae"
    ).fetchall()
    secoes = {s: n for _, _, s, n in cnaes}

    itens = con.execute(
        """SELECT item_id, tipo_curto, beneficio_fiscal, tributo, fundamento_legal, regime
           FROM dim_item ORDER BY item_id"""
    ).fetchall()

    macro = con.execute(
        "SELECT ano, ipca_indice_medio, pib_nominal_reais FROM mart_ano ORDER BY ano"
    ).fetchall()

    # ---------------------------------------------------------------- DIM --
    estabs = con.execute(
        "SELECT estab_id, cnpj, razao_social, nome_fantasia, cnae, municipio, uf "
        "FROM dim_estab ORDER BY estab_id"
    ).fetchall()
    n_estab = len(estabs)
    classificacoes = classificar_estabelecimentos(estabs)
    setores_detalhados = sorted({r['setor_detalhado'] for r in classificacoes})
    setor_id = {s: i for i, s in enumerate(setores_detalhados)}
    evidencias_setor = sorted({(r['regra'], r['fonte'], r['evidencia']) for r in classificacoes})
    evidencia_id = {s: i for i, s in enumerate(evidencias_setor)}
    setores_estab = [[setor_id[r['setor_detalhado']],
                     evidencia_id[(r['regra'], r['fonte'], r['evidencia'])]]
                    for r in classificacoes]
    classificacao = {"versao": VERSION, "setores": setores_detalhados,
                     "evidencias": evidencias_setor, "estabelecimentos": setores_estab}
    if "--somente-setores" in sys.argv:
        # Edição cadastral: preservar integralmente os dados fiscais já publicados.
        with open(OUT, encoding="utf-8") as f:
            payload = json.load(f)
        dim_existente = gzip.decompress(base64.b64decode(payload["dim"])).decode().splitlines()
        assert len(dim_existente) == n_estab
        assert all(l.split("\t")[0] == e[1] and l.split("\t")[3] == e[4]
                   for l, e in zip(dim_existente, estabs)), "Cadastro do payload difere do banco"
        payload["classificacao_setorial"] = classificacao
        with open(OUT, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, separators=(",", ":"))
        print(f"Classificação atualizada para {n_estab} CNPJs; dados fiscais preservados.")
        return
    dim = []
    for eid, cnpj, razao, fant, cnae, mun, uf in estabs:
        assert eid == len(dim), "estab_id precisa ser contíguo e começar em 0"
        f = fant if fant and fant != razao else ""
        dim.append(f"{cnpj}\t{razao}\t{f}\t{cnae}\t{mun_id[(mun, uf)]}")

    # --------------------------------------------------------------- FATO --
    fato = con.execute(
        "SELECT estab_id, list(ano - %d ORDER BY ano), list(valor ORDER BY ano) "
        "FROM fato_empresa_ano GROUP BY estab_id ORDER BY estab_id" % ANO0
    ).fetchall()
    linhas_fato = [""] * n_estab
    n_fato = 0
    for eid, anos, vals in fato:
        linhas_fato[eid] = " ".join(f"{a} {round(v)}" for a, v in zip(anos, vals))
        n_fato += len(anos)

    # --------------------------------------------------------------- ITEM --
    # Uma linha por estabelecimento economiza repetir o id em 711 mil linhas.
    item_rows = con.execute(
        """SELECT estab_id, ano - %d, item_id, valor
           FROM fato_item_ano ORDER BY estab_id, ano, item_id""" % ANO0
    ).fetchall()
    linhas_item = [""] * n_estab
    atual, buf = -1, []
    for eid, a, it, v in item_rows:
        if eid != atual:
            if atual >= 0:
                linhas_item[atual] = " ".join(buf)
            atual, buf = eid, []
        buf.append(f"{a} {it} {round(v)}")
    if atual >= 0:
        linhas_item[atual] = " ".join(buf)

    # ---------------------------------------------------------------- AGG --
    agg = con.execute(
        """SELECT f.ano - %d, f.item_id, c.secao, coalesce(e.uf, ''), sum(f.valor)
           FROM fato_item_ano f
           JOIN dim_estab e USING (estab_id)
           JOIN dim_cnae  c ON c.cnae = e.cnae
           GROUP BY 1, 2, 3, 4
           ORDER BY 1, 2, 3, 4""" % ANO0
    ).fetchall()
    linhas_agg = [f"{a}\t{i}\t{s}\t{u}\t{round(v)}" for a, i, s, u, v in agg]

    # ------------------------------------------------------------ montagem --
    b_dim, s_dim = blob(dim)
    b_fato, s_fato = blob(linhas_fato)
    b_item, s_item = blob(linhas_item)
    b_agg, s_agg = blob(linhas_agg)

    manifest = os.path.join(ROOT, "data", "raw", "manifest.tsv")
    last_mod = ""
    if os.path.exists(manifest):
        with open(manifest, encoding="utf-8") as f:
            linhas = [l.rstrip("\n").split("\t") for l in f][1:]
        if linhas:
            last_mod = linhas[-1][2]

    payload = {
        "meta": {
            "ano0": ANO0,
            "anos": [a for a, _, _ in macro],
            "ano_parcial": ANO_PARCIAL,
            "fonte": "Portal da Transparência / CGU — Renúncias Fiscais",
            "url": "https://portaldatransparencia.gov.br/download-de-dados/renuncias",
            "arquivo_atualizado_em": last_mod,
            "extraido_em": datetime.date.today().isoformat(),
            "n_itens": len(item_rows),
            "n_fundamentos": con.execute(
                "SELECT count(DISTINCT fundamento_legal) FROM dim_item").fetchone()[0],
            "n_regimes": con.execute(
                "SELECT count(DISTINCT regime) FROM dim_item").fetchone()[0],
        },
        "macro": [[a, round(i, 4), p] for a, i, p in macro],
        "secoes": secoes,
        "classificacao_setorial": classificacao,
        "cnae": [[c, d, s] for c, d, s, _ in cnaes],
        "mun": [[m, u] for m, u in muns],
        "item": [[t, b, tr, f, r] for _, t, b, tr, f, r in itens],
        "dim": b_dim,
        "fato": b_fato,
        "itens": b_item,
        "agg": b_agg,
    }

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, separators=(",", ":"))

    mb = lambda n: f"{n/1e6:.2f} MB"
    print(f"DIM   {len(dim):>7} linhas   gz {mb(s_dim)}   b64 {mb(s_dim*4/3)}")
    print(f"FATO  {n_fato:>7} pontos   gz {mb(s_fato)}   b64 {mb(s_fato*4/3)}")
    print(f"ITEM  {len(item_rows):>7} trincas  gz {mb(s_item)}   b64 {mb(s_item*4/3)}   "
          f"({len(itens)} itens distintos, cobertura total)")
    print(f"AGG   {len(linhas_agg):>7} linhas   gz {mb(s_agg)}   b64 {mb(s_agg*4/3)}")
    print(f"payload.json  {mb(os.path.getsize(OUT))}")


if __name__ == "__main__":
    main()
