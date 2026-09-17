#!/usr/bin/env python3
"""Exporta a apresentação na referência IPCA documentada, preservando o snapshot fiscal."""
import json
import re
import hashlib
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
out = dict(base=reference['base'],base_mes=reference['base_mes'],indice_base=base,referencia=reference,
 fonte_ipca=URL,fonte_ipca_pagina=18,fonte_ipca_sha256=hashlib.sha256(PDF.read_bytes()).hexdigest(),
 formula=f"nominal do período × IPCA {reference['base_mes']} ÷ média dos índices dos meses cobertos (jan–dez/2015–2023; jan–jun/2024)",
 anos=annual,total_real=total,total_nominal=sum(r['nominal'] for r in annual),
 tipos=[dict(tipo=t,real=v,participacao=v/total) for t,v in sorted(by_type.items(),key=lambda x:-x[1])],
 cnpjs=con.execute('select count(*) from dim_estab').fetchone()[0],
 razao_base_media2023=base/means[2023],razao_base_media2024=base/means[2024])
(ROOT/'artifact/apresentacao.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
(QA/'validacao.json').write_text(json.dumps(dict(total_real=total,soma_tipos=sum(by_type.values()),indice_base=base, medias_2020_2024_conferidas=True,tipos=out['tipos'],fatores=[{'ano':r['ano'],'fator':r['fator']} for r in annual]),ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:out[k] for k in ['total_real','indice_base','razao_base_media2023','razao_base_media2024','tipos']},ensure_ascii=False,indent=2))
