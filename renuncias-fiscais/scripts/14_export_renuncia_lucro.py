#!/usr/bin/env python3
"""Exporta a comparação histórica autorizada, sem novas consultas financeiras."""
from pathlib import Path
from decimal import Decimal
import csv,json,re
R=Path(__file__).resolve().parents[1];Q=R/'qa/renuncia-lucro';F=Q/'fontes'
def read(name):return list(csv.DictReader((F/name).open(encoding='utf-8')))
rank={x['label']:x for x in read('ranking_reproduzido.csv')}
audit={x['label']:x for x in read('auditoria_yfinance.csv')}
volvo=json.loads((F/'volvo_adicionada.json').read_text());rows=[]
for x in read('tabela_financeira_20.csv'):
    name=x['beneficiario'];a=audit.get(name);f=rank.get(name)
    if a:
        match=re.search(r'EBITDA ([\d.]+)',x['ebitda_exibido'])
        e=float(Decimal(match[1])*10**9) if match else None
        nominal=float(f['renuncia_2023_nominal']);ren=float(f['renuncia_2023_corrigida'])
        date=a['data_escolhida'];currency=a['moeda_apos_heuristica'];fx=float(a['cambio_aplicado']) if a['cambio_aplicado'] else None
        original=float(a['ebitda_bruto']) if a['ebitda_bruto'] else None
        converted=float(a['ebitda_brl_codigo']) if a['ebitda_brl_codigo'] else None
        scope='Companhia listada; escopo não validado por CNPJ' if a['origem']=='entidade' else 'Matriz/grupo global; aproximação para a empresa brasileira'
        if name=='Modec':scope='Mitsui & Co.; aproximação do autor, vínculo não validado nesta auditoria'
        if name=='Syngenta Brasil':scope='FMC; aproximação setorial, não é o EBITDA da Syngenta'
        if e is None:scope='Sem ticker configurado' if not x['ticker'] else 'DRE indisponível na consulta arquivada'
        reason=f['razao_social'];origin='EBITDA histórico publicado pelo Carabetta, arredondado a R$ 0,1 bilhão'
    else:
        assert name=='Volvo Brasil'
        e=volvo['ebitda_brl'];nominal=float(volvo['renuncia_2023_nominal']);ren=float(volvo['renuncia_2023_corrigida'])
        date=volvo['data_final_exercicio'];currency=volvo['moeda'];fx=volvo['taxa_brl'];original=volvo['ebitda_original'];converted=e
        scope='Volvo Group; aproximação para a empresa brasileira';reason=volvo['razao_social'];origin='Consulta Yahoo de 17/09/2026, regra original; precisão preservada'
    meta={}
    if x['ticker']:
        p=F/'yahoo'/x['ticker']/'meta.json'
        if p.exists():meta=json.loads(p.read_text())
    rows.append(dict(linha=int(x['linha']),posicao_fiscal=int(x['posicao_ranking_fiscal']),beneficiario=name,razao_social=reason,ticker=x['ticker'],renuncia_nominal=nominal,renuncia_comparada=ren,ebitda=e,percentual=ren/e*100 if e and e>0 else None,percentual_historico=x['renuncia_ebitda_pct_exibido'],escopo=scope,data_final=date,moeda=currency,cambio=fx,ebitda_yahoo_original=original,ebitda_reconsulta_brl=converted,origem=origin,consulta=meta.get('consulta_utc',''),emissor=meta.get('info',{}).get('longName',''),moeda_metadado=a['moeda_info'] if a else currency))
assert len(rows)==20 and sum(r['ebitda'] is not None for r in rows)==18
assert len({r['razao_social'] for r in rows})==20
factor=rows[0]['renuncia_comparada']/rows[0]['renuncia_nominal']
assert all(abs(r['renuncia_comparada']/r['renuncia_nominal']-factor)<1e-12 for r in rows)
data=dict(consulta='17/09/2026',fator_2023=factor,linhas=rows)
(R/'artifact/renuncia-lucro.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
out=R.parent/'docs/renuncias-fiscais/evidencias/renuncia-lucro.csv'
with out.open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
print(f'{len(rows)} beneficiários; 18 EBITDAs; fator {factor:.12f}; percentuais recalculados.')
