#!/usr/bin/env python3
"""Exporta a apresentação na referência IPCA documentada, preservando o snapshot fiscal."""
import json
import re
import hashlib
import math
from classificacao_setorial import classificar_estabelecimentos
from pathlib import Path
from collections import defaultdict
import duckdb
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
QA = ROOT / 'qa/apresentacao'
PDF = QA / 'ipca-inpc-202412.pdf'
URL = 'https://ftp.ibge.gov.br/Precos_Indices_de_Precos_ao_Consumidor/IPCA/Fasciculo_Indicadores_IBGE/2024/ipca-inpc_202412caderno.pdf'
text = PdfReader(PDF).pages[17].extract_text()
# Página 18: série histórica IPCA, não a tabela INPC da página 21.
monthly = defaultdict(list)
year = None
for line in text.splitlines():
    m = re.match(r'(?:(202[0-4])\s+)?(JAN|FEV|MAR|ABR|MAI|JUN|JUL|AGO|SET|OUT|NOV|DEZ)\s+(\d+,\d+)', line.strip())
    if m:
        if m[1]: year = int(m[1])
        monthly[year].append(float(m[3].replace(',', '.')))
assert all(len(monthly[y]) == 12 for y in range(2020, 2025))
reference = json.loads((ROOT/'data/macro/referencia-ipca.json').read_text())
assert reference['indice'] == 'IPCA'
base = reference['indice_base']
con = duckdb.connect(str(ROOT / 'renuncias.duckdb'), read_only=True)
macro = con.execute('SELECT ano, valor, ipca_indice_medio FROM mart_ano ORDER BY ano').fetchall()
assert [r[0] for r in macro] == list(range(2015,2025))
for y, _, idx in macro:
    if y in monthly: assert abs(sum(monthly[y])/12-idx) < 0.0001
means = {y:idx for y,_,idx in macro}
coverage = json.loads((ROOT/'data/macro/cobertura-deflacao.json').read_text())['anos']
assert set(coverage) == {str(y) for y in means}, 'Cobertura precisa ser explícita para todos os anos'
origins = {}
for y, idx in means.items():
    first, last = coverage[str(y)]
    assert 1 <= first <= last <= 12
    if (first, last) == (1, 12):
        origins[y] = idx
    else:
        assert y in monthly, f'Faltam índices mensais para o período parcial {y}'
        covered = monthly[y][first-1:last]
        assert len(covered) == last-first+1
        origins[y] = sum(covered)/len(covered)

rows = con.execute('''SELECT f.ano, i.tipo_curto, sum(f.valor) FROM fato_item_ano f
 JOIN dim_item i USING(item_id) GROUP BY 1,2 ORDER BY 1,2''').fetchall()
by_type = defaultdict(float)
by_year = defaultdict(float)
for y, tipo, nominal in rows:
    by_type[tipo] += nominal * base / origins[y]
    by_year[y] += nominal
annual = []
for y, nominal, idx in macro:
    assert abs(by_year[y]-nominal) < 0.05, (y, by_year[y]-nominal)
    annual.append(dict(ano=y,nominal=nominal,real=nominal*base/origins[y],fator=base/origins[y],indice_medio=idx,indice_origem=origins[y],meses_origem=coverage[str(y)],parcial=y==2024))
total = sum(r['real'] for r in annual)
assert abs(sum(by_type.values())-total)<0.05
# Hierarquia monetária: cada linha pertence a um tipo, benefício e tributo.
hierarchy = defaultdict(float)
for y, tipo, beneficio, tributo, value in con.execute("""SELECT f.ano,
 coalesce(nullif(i.tipo_curto,''),'Sem informação'),
 coalesce(nullif(i.beneficio_fiscal,''),'Sem informação'),
 coalesce(nullif(i.tributo,''),'Sem informação'), sum(f.valor)
 FROM fato_item_ano f JOIN dim_item i USING(item_id) GROUP BY 1,2,3,4""").fetchall():
    hierarchy[(tipo,beneficio,tributo)] += value * base / origins[y]
assert abs(sum(hierarchy.values()) - total) < 0.05
for tipo, expected in by_type.items():
    assert abs(sum(v for (t,b,tr),v in hierarchy.items() if t == tipo) - expected) < 0.05
out = dict(base=reference['base'],base_mes=reference['base_mes'],indice_base=base,referencia=reference,
 fonte_ipca=URL,fonte_ipca_pagina=18,fonte_ipca_sha256=hashlib.sha256(PDF.read_bytes()).hexdigest(),
 formula=f"nominal do período × IPCA {reference['base_mes']} ÷ média dos índices dos meses cobertos (jan–dez/2015–2023; jan–jun/2024)",
 hierarquia=[dict(tipo=t,beneficio=b,tributo=tr,real=v) for (t,b,tr),v in sorted(hierarchy.items())],
 anos=annual,total_real=total,total_nominal=sum(r['nominal'] for r in annual),
 tipos=[dict(tipo=t,real=v,participacao=v/total) for t,v in sorted(by_type.items(),key=lambda x:-x[1])],
 cnpjs=con.execute('select count(*) from dim_estab').fetchone()[0],
 razao_base_media2023=base/means[2023],razao_base_media2024=base/means[2024])
# Concentração por raiz, preservando o valor do identificador inválido no total.
estabs = con.execute("SELECT estab_id,cnpj,razao_social,nome_fantasia,cnae,municipio,uf FROM dim_estab ORDER BY estab_id").fetchall()
classification = {r['estab_id']:r['setor'] for r in classificar_estabelecimentos(estabs)}
by_id = {r[0]:r for r in estabs}
roots = {}
sectors = defaultdict(lambda:[0.0]*len(annual))
invalid = 0.0
estab_nominal = dict(con.execute('SELECT estab_id,sum(valor) FROM fato_empresa_ano GROUP BY 1').fetchall())
for eid,year,value in con.execute('SELECT estab_id,ano,valor FROM fato_empresa_ano').fetchall():
    corrected = value*base/origins[year]
    sectors[classification[eid]][year-2015] += corrected
    cnpj = by_id[eid][1]
    if not re.fullmatch(r'[0-9]{14}',cnpj):
        invalid += corrected
        continue
    root = cnpj[:8]
    r = roots.setdefault(root,dict(raiz=root,real=0.0,membros=set()))
    r['real'] += corrected
    r['membros'].add(eid)
negative = [r for r in roots.values() if r['real']<0]
rank = sorted(roots.values(),key=lambda r:-r['real'])
assert abs(sum(r['real'] for r in rank)+invalid-total)<0.05
n = len(rank); n1 = math.ceil(n/100)
top20=[]
for r in rank[:20]:
    principal = max(sorted(r['membros']),key=lambda e:estab_nominal[e])
    top20.append(dict(raiz=r['raiz'],nome=by_id[principal][2],real=r['real'],cnpjs=len(r['membros']),participacao=r['real']/total))
sector_rows=[dict(setor=name,valores=vals,real=sum(vals),participacao=sum(vals)/total) for name,vals in sectors.items()]
sector_rows.sort(key=lambda r:-r['real'])
for i,year in enumerate(annual):
    assert abs(sum(r['valores'][i] for r in sector_rows)-year['real'])<.05
# Seções CNAE: mesma granularidade de estabelecimento, período e deflação da classificação editorial.
cnae_series = defaultdict(lambda: [0.0]*len(annual))
for year, name, value in con.execute("""SELECT f.ano,
 coalesce(nullif(c.secao_nome,''),'Sem informação'), sum(f.valor)
 FROM fato_empresa_ano f JOIN dim_estab e USING(estab_id)
 LEFT JOIN dim_cnae c ON e.cnae=c.cnae GROUP BY 1,2""").fetchall():
    cnae_series[name][year-2015] += value*base/origins[year]
cnae_rows = sorted([dict(setor=name,valores=vals,real=sum(vals),participacao=sum(vals)/total)
                    for name,vals in cnae_series.items()], key=lambda r:-r['real'])
for i, year in enumerate(annual):
    assert abs(sum(r['valores'][i] for r in cnae_rows)-year['real']) < .05
# Concentração cumulativa, com/sem a pessoa jurídica Petrobras (raiz 33000167).
petrobras = roots['33000167']['real']
concentracao = {}
for incluir, key in [(True, 'com_petrobras'), (False, 'sem_petrobras')]:
    universo = rank if incluir else [r for r in rank if r['raiz'] != '33000167']
    denominador = total if incluir else total-petrobras
    assert abs(sum(r['real'] for r in universo)+invalid-denominador) < .05
    faixas = []
    for numerador, divisor in [(1,1000),(1,100),(5,100),(10,100)]:
        quantidade = (len(universo)*numerador+divisor-1)//divisor
        valor = sum(r['real'] for r in universo[:quantidade])
        faixas.append(dict(percentual_beneficiarios=100*numerador/divisor,
                          quantidade=quantidade,percentual_efetivo=quantidade/len(universo)*100,
                          valor=valor,percentual_renuncias=valor/denominador*100))
    concentracao[key] = dict(n_beneficiarios=len(universo),total=denominador,faixas=faixas)
assert concentracao['com_petrobras']['n_beneficiarios']-concentracao['sem_petrobras']['n_beneficiarios']==1
out['beneficiarios']=dict(concentracao=concentracao,valor_petrobras=petrobras,n_raizes=n,n_raizes_negativas=len(negative),saldo_negativo=sum(r['real'] for r in negative),n_top1=n1,pct_empresas_top1=n1/n*100,
 pct_valor_top1=sum(r['real'] for r in rank[:n1])/total*100,
 pct_top10=sum(r['real'] for r in rank[:10])/total*100,
 pct_top100=sum(r['real'] for r in rank[:100])/total*100,
 valor_identificador_invalido=invalid,top20=top20,setores=sector_rows,setores_cnae=cnae_rows)
(ROOT/'artifact/apresentacao.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
(QA/'validacao.json').write_text(json.dumps(dict(total_real=total,soma_tipos=sum(by_type.values()),indice_base=base, medias_2020_2024_conferidas=True,tipos=out['tipos'],fatores=[{'ano':r['ano'],'fator':r['fator']} for r in annual]),ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:out[k] for k in ['total_real','indice_base','razao_base_media2023','razao_base_media2024','tipos']},ensure_ascii=False,indent=2))
