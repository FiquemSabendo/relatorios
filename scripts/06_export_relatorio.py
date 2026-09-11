#!/usr/bin/env python3
"""Agregados do relatório em abas (docs/index.html) a partir de renuncias.duckdb.

Tudo que o relatório mostra sai daqui: relatorio/dados.json (~100 KB). Nada é
calculado à mão no HTML — os textos são montados em JS a partir destes números.

Convenções:
  * valores em reais correntes ("nominal") e em reais de ANO_BASE ("real"),
    deflacionados pela média anual do número-índice do IPCA;
  * "% do PIB" = nominal do ano ÷ PIB nominal do ano (mesma base de preços dos
    dois lados — o deflator não entra nessa conta);
  * a década inteira (2015–2024) entra nos acumulados, como no Portal; 2024 é
    parcial e aparece sempre sinalizado.
"""
import datetime as dt
import json
import os
import re

import duckdb

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, "renuncias.duckdb")
OUT = os.path.join(ROOT, "relatorio", "dados.json")
ANO_BASE = 2025          # último ano com 12 meses de IPCA
ANO_PARCIAL = 2024
ULTIMO_COMPLETO = 2023

# regime (scripts/03_build_db.sql) -> tema de política pública
TEMAS = {
    "Regimes aduaneiros especiais (importação)": [
        "Regimes aduaneiros especiais (PIS/Cofins)", "Admissão temporária",
        "Entreposto e depósito aduaneiro", "Loja franca", "Acordos comerciais e cotas"],
    "Industrialização regional (ZFM, Sudam/Sudene)": [
        "Zona Franca de Manaus", "Sudam/Sudene", "Finor/Finam"],
    "Exportação e cadeias globais (Recof, Drawback)": [
        "Recof (entreposto industrial)", "Drawback", "Recap (exportadoras)"],
    "Petróleo, gás e energia (Repetro)": ["Repetro (petróleo e gás)", "Gás natural e energia"],
    "Alimentos e insumos agropecuários": ["Desoneração de alimentos e insumos agrícolas"],
    "Saúde, cultura, educação e social": [
        "Farmacêuticos e químicos", "Pronon (oncologia)", "Pronas/PCD (pessoa com deficiência)",
        "Lei Rouanet (Pronac)", "Prouni", "PAT (alimentação do trabalhador)",
        "Incentivo ao Desporto", "Fundos da Criança e do Adolescente", "Fundos do Idoso",
        "Empresa Cidadã", "Atividade audiovisual", "Livros e imprensa", "Perse (setor de eventos)"],
    "Indústria, infraestrutura e tecnologia": [
        "Setor aeronáutico", "Autopeças e máquinas agrícolas", "Setor naval e portuário",
        "Padis (semicondutores)", "Repes (software)", "Rota 2030", "Reidi (infraestrutura)",
        "Reporto (portos)", "Ciência e pesquisa"],
    "Estado, organismos internacionais e eleições": [
        "Entes públicos e organismos internacionais", "Horário Eleitoral"],
    "Sem mecanismo identificado (\"outras isenções\")": [
        "Outras isenções não capituladas", "Outros fundamentos de importação"],
}
TEMA_DE = {r: t for t, rs in TEMAS.items() for r in rs}

# CNPJs da administração pública direta e autarquias (razão social) — proxy por texto
RE_PUBLICO = (r"MINISTERIO|COMANDO D[AO] |UNIVERSIDADE FEDERAL|FUNDACAO OSWALDO|INSTITUTO FEDERAL"
              r"|AGENCIA NACIONAL|SUPERINTENDENCIA|SECRETARIA D|PREFEITURA|GOVERNO DO ESTADO"
              r"|TRIBUNAL|EMPRESA BRASILEIRA DE|CONSELHO NACIONAL|FUNDACAO DE AMPARO|FUNDACAO EZEQUIEL")

con = duckdb.connect(DB, read_only=True)
q = lambda sql, *p: con.execute(sql, p).fetchall()

# fator de deflação por ano ------------------------------------------------
idx = dict(q("select ano, ipca_indice_medio from macro_ipca"))
base = idx[ANO_BASE]
fator = {a: base / idx[a] for a in range(2015, 2025)}
con.execute("create temp table f as select * from (values " +
            ",".join(f"({a},{v!r})" for a, v in fator.items()) + ") t(ano, f)")

def rows(sql, cols):
    return [dict(zip(cols, r)) for r in q(sql)]

D = {"meta": {
    "ano_base": ANO_BASE, "ano_parcial": ANO_PARCIAL, "ultimo_completo": ULTIMO_COMPLETO,
    "fator": {str(a): round(v, 6) for a, v in fator.items()},
    "extraido_em": dt.date.today().isoformat(),
}}

# manifesto da extração
man = os.path.join(ROOT, "data", "raw", "manifest.tsv")
if os.path.exists(man):
    linhas = [l.split("\t") for l in open(man, encoding="utf-8").read().strip().splitlines()[1:]]
    D["meta"]["arquivo_atualizado_em"] = max(l[2] for l in linhas)
    D["meta"]["baixado_em"] = max(l[3] for l in linhas)

# 1. série anual ---------------------------------------------------------
D["ano"] = rows("""
  select m.ano, m.valor, m.valor*f.f, m.n_estab, m.n_grupos, m.pib_nominal_reais,
         100.0*m.valor/m.pib_nominal_reais
  from mart_ano m join f using(ano) order by ano""",
  ["ano", "nominal", "real", "n_cnpj", "n_grupos", "pib", "pct_pib"])

# 2. tipo de renúncia por ano ---------------------------------------------
D["tipo_ano"] = rows("""
  select v.ano, i.tipo_curto, sum(v.valor), sum(v.valor*f.f)
  from fato_item_ano v join dim_item i using(item_id) join f using(ano)
  group by 1,2 order by 1,2""", ["ano", "tipo", "nominal", "real"])

# 3. detalhe do último ano completo: tipo -> benefício -> tributo ----------
D["arvore_2023"] = rows(f"""
  select i.tipo_curto, i.beneficio_fiscal, i.tributo, sum(v.valor)
  from fato_item_ano v join dim_item i using(item_id)
  where v.ano = {ULTIMO_COMPLETO} group by 1,2,3 order by 4 desc""",
  ["tipo", "beneficio", "tributo", "nominal"])

# 4. quem recebe ----------------------------------------------------------
con.execute("""create temp table est as
  select e.estab_id, e.cnpj, e.cnpj_raiz, e.razao_social, e.uf, e.municipio, c.secao_nome,
         sum(v.valor) nominal, sum(v.valor*f.f) vreal
  from fato_empresa_ano v join dim_estab e using(estab_id) join dim_cnae c on c.cnae = e.cnae
  join f using(ano) group by all""")
con.execute("""create temp table grp as
  select cnpj_raiz, arg_max(razao_social, vreal) nome, count(*) n_cnpj, sum(nominal) nominal,
         sum(vreal) vreal, arg_max(uf, vreal) uf, arg_max(municipio, vreal) municipio,
         arg_max(secao_nome, vreal) setor
  from est group by 1""")
tot_real = q("select sum(vreal) from est")[0][0]
tot_nom = q("select sum(nominal) from est")[0][0]
D["total"] = {"nominal": tot_nom, "real": tot_real,
              "n_cnpj": q("select count(*) from est")[0][0],
              "n_grupos": q("select count(*) from grp")[0][0]}

D["top_grupos"] = rows("""
  select nome, cnpj_raiz, n_cnpj, nominal, vreal, uf, municipio, setor
  from grp order by vreal desc limit 25""",
  ["nome", "raiz", "n_cnpj", "nominal", "real", "uf", "municipio", "setor"])
D["top_razoes"] = rows("""
  select razao_social, count(*) n, sum(nominal), sum(vreal) from est
  group by 1 order by 4 desc limit 20""", ["nome", "n_cnpj", "nominal", "real"])

def cum(tabela):
    r = q(f"select vreal from {tabela} order by vreal desc")
    vals = [x[0] for x in r]
    n = len(vals); acc = 0; out = []
    marcas = [1, 5, 10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000, n]
    for k, v in enumerate(vals, 1):
        acc += v
        if k in marcas or k == n:
            out.append({"k": k, "pct_ent": 100.0 * k / n, "pct_val": 100.0 * acc / tot_real})
    return out
D["pareto_cnpj"] = cum("est")
D["pareto_grupo"] = cum("grp")

# evolução dos maiores grupos ano a ano (real)
top8 = [r["raiz"] for r in D["top_grupos"][:8]]
lst = ",".join(f"'{r}'" for r in top8)
D["evolucao_top"] = rows(f"""
  select v.ano, case when e.cnpj_raiz in ({lst}) then e.cnpj_raiz else '__demais' end g,
         sum(v.valor*f.f)
  from fato_empresa_ano v join dim_estab e using(estab_id) join f using(ano)
  group by 1,2 order by 1""", ["ano", "raiz", "real"])
D["evolucao_top_nomes"] = {r["raiz"]: r["nome"] for r in D["top_grupos"][:8]}

# setor público (proxy por razão social)
D["publico"] = {
    "n": q(f"select count(*) from est where regexp_matches(razao_social, '{RE_PUBLICO}')")[0][0],
    "real": q(f"select sum(vreal) from est where regexp_matches(razao_social, '{RE_PUBLICO}')")[0][0],
    "lista": rows(f"""select razao_social, uf, sum(vreal), count(*) from est
      where regexp_matches(razao_social, '{RE_PUBLICO}') group by 1,2 order by 3 desc limit 8""",
      ["nome", "uf", "real", "n_cnpj"]),
}
D["sem_cnae"] = {"real": q("select sum(vreal) from est where secao_nome = 'Sem informação'")[0][0],
                 "n_cnpj": q("select count(*) from est where secao_nome = 'Sem informação'")[0][0]}

# 5. onde e setores -------------------------------------------------------
D["uf"] = rows("select uf, sum(nominal), sum(vreal), count(*) from est group by 1 order by 3 desc",
               ["uf", "nominal", "real", "n_cnpj"])
D["municipio"] = rows("""select municipio, uf, sum(vreal), count(*) from est
  group by 1,2 order by 3 desc limit 15""", ["municipio", "uf", "real", "n_cnpj"])
D["setor"] = rows("select secao_nome, sum(nominal), sum(vreal), count(*) from est group by 1 order by 3 desc",
                  ["setor", "nominal", "real", "n_cnpj"])
D["setor_ano"] = rows("""
  select v.ano, c.secao_nome, sum(v.valor)
  from fato_empresa_ano v join dim_estab e using(estab_id) join dim_cnae c on c.cnae = e.cnae
  group by 1,2 order by 1""", ["ano", "setor", "nominal"])
# Sudam/Sudene: onde está registrado
D["sudam_uf"] = rows("""
  select e.uf, sum(v.valor*f.f) from fato_item_ano v join dim_item i using(item_id)
  join dim_estab e using(estab_id) join f using(ano)
  where i.regime = 'Sudam/Sudene' group by 1 order by 2 desc limit 10""", ["uf", "real"])
D["sudam_total"] = q("""select sum(v.valor*f.f) from fato_item_ano v join dim_item i using(item_id)
  join f using(ano) where i.regime = 'Sudam/Sudene'""")[0][0]

# 6. o que prioriza -------------------------------------------------------
D["regime"] = rows("""
  select i.regime, sum(v.valor), sum(v.valor*f.f), count(distinct e.cnpj_raiz)
  from fato_item_ano v join dim_item i using(item_id) join dim_estab e using(estab_id) join f using(ano)
  group by 1 order by 3 desc""", ["regime", "nominal", "real", "n_grupos"])
for r in D["regime"]:
    r["tema"] = TEMA_DE.get(r["regime"], "Sem mecanismo identificado (\"outras isenções\")")
D["regime_ano"] = rows("""
  select v.ano, i.regime, sum(v.valor*f.f)
  from fato_item_ano v join dim_item i using(item_id) join f using(ano)
  group by 1,2 order by 1""", ["ano", "regime", "real"])
D["fundamento"] = rows("""
  select i.fundamento_legal, i.tipo_curto, sum(v.valor*f.f)
  from fato_item_ano v join dim_item i using(item_id) join f using(ano)
  group by 1,2 order by 3 desc limit 15""", ["fundamento", "tipo", "real"])
D["n_fundamentos"] = q("select count(distinct fundamento_legal) from dim_item")[0][0]
D["n_regimes"] = q("select count(distinct regime) from dim_item")[0][0]

os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump(D, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
print(f"{OUT}  {os.path.getsize(OUT)/1e3:.0f} KB")
for a in D["ano"]:
    print(f"  {a['ano']}  nominal {a['nominal']/1e9:6.1f}  real {a['real']/1e9:6.1f}  %PIB {a['pct_pib']:.2f}")
print(f"  total {tot_nom/1e9:.1f} bi nominal / {tot_real/1e9:.1f} bi reais de {ANO_BASE}")
