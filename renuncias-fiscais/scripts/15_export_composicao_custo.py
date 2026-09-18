#!/usr/bin/env python3
"""Composição auditável e comparações fiscais de 2023, preservando fontes históricas."""
from pathlib import Path
from collections import defaultdict
from datetime import datetime
import json, hashlib, requests, duckdb, openpyxl
ROOT=Path(__file__).resolve().parents[1]
Q=ROOT/'qa/composicao-custo';F=Q/'fontes';F.mkdir(parents=True,exist_ok=True)
URL='https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/thot/arquivos/publicacoes/48787_1551088/anexos/22121_755246/serie_historica_dez23.xlsx'
PDF='https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/thot/arquivos/publicacoes/48787_1551088/boletim_dez23.pdf'
for name,url in [('rtn-dez2023.xlsx',URL),('rtn-dez2023.pdf',PDF)]:
 p=F/name
 if not p.exists():
  r=requests.get(url,timeout=60);r.raise_for_status();p.write_bytes(r.content)
a=json.loads((ROOT/'artifact/apresentacao.json').read_text());fatores={r['ano']:r['fator'] for r in a['anos']}
c=duckdb.connect(str(ROOT/'renuncias.duckdb'),read_only=True)
# Temas são editoriais. Mecanismos de finalidade genérica ficam sem tema setorial inferido.
groups={
 'Desenvolvimento regional':['Sudam/Sudene','Finor/Finam','Zona Franca de Manaus'],
 'Educação':['Prouni'],
 'Cultura, esporte e eventos':['Lei Rouanet (Pronac)','Atividade audiovisual','Livros e imprensa','Incentivo ao Desporto','Perse (setor de eventos)'],
 'Proteção social e trabalho':['Empresa Cidadã','Fundos do Idoso','Fundos da Criança e do Adolescente','PAT (alimentação do trabalhador)'],
 'Saúde e inclusão':['Pronon (oncologia)','Pronas/PCD (pessoa com deficiência)'],
 'Ciência, tecnologia e inovação':['Ciência e pesquisa','Repes (software)','Padis (semicondutores)'],
 'Energia, petróleo e gás':['Repetro (petróleo e gás)','Gás natural e energia'],
 'Infraestrutura e logística':['Reidi (infraestrutura)','Reporto (portos)','Setor naval e portuário'],
 'Indústria e cadeias produtivas':['Setor aeronáutico','Autopeças e máquinas agrícolas','Rota 2030','Farmacêuticos e químicos'],
 'Alimentos e insumos agrícolas':['Desoneração de alimentos e insumos agrícolas'],
 'Exportação e comércio exterior':['Drawback','Recof (entreposto industrial)','Recap (exportadoras)','Acordos comerciais e cotas','Loja franca','Entreposto e depósito aduaneiro','Admissão temporária'],
 'Administração pública e relações internacionais':['Entes públicos e organismos internacionais'],
 'Processo eleitoral':['Horário Eleitoral'],
 'Tema não determinado':['Regimes aduaneiros especiais (PIS/Cofins)','Outras isenções não capituladas','Outros fundamentos de importação']}
mapping={reg:tema for tema,regs in groups.items() for reg in regs}
items=[]
for row in c.execute('select item_id,tipo_curto,beneficio_fiscal,tributo,fundamento_legal,regime from dim_item order by item_id').fetchall():
 id,tipo,benef,trib,fund,reg=row
 assert reg in mapping,reg
 items.append(dict(id=id,tipo=tipo,beneficio=benef or 'Sem informação',tributo=trib or 'Sem informação',fundamento=fund or 'Sem informação',mecanismo=reg,tema=mapping[reg],nominal=[0]*10,real=[0]*10))
byid={r['id']:r for r in items}
for id,ano,valor in c.execute('select item_id,ano,sum(valor) from fato_item_ano group by 1,2').fetchall():
 byid[id]['nominal'][ano-2015]=valor;byid[id]['real'][ano-2015]=valor*fatores[ano]
checks=[]
for i,yr in enumerate(a['anos']):
 for medida in ['nominal','real']:
  diff=sum(r[medida][i] for r in items)-yr[medida]
  assert abs(diff)<.01,(i,medida,diff)
  checks.append(dict(ano=yr['ano'],medida=medida,diferenca=diff))
w=openpyxl.load_workbook(F/'rtn-dez2023.xlsx',data_only=True)
s=w['2.2'];m=w['1.2'];col=next(x.column for x in s[5] if x.value==2023)
months=[x.column for x in m[5] if isinstance(x.value,datetime) and x.value.year==2023];assert len(months)==12
assert 'Valores Correntes' in s.cell(3,1).value
specs=[(141,'Bolsa Família e Auxílio Brasil','Transferências do programa na rubrica do RTN; inclui a transição entre os programas em 2023.'),(79,'BPC e Renda Mensal Vitalícia','Benefícios de Prestação Continuada da LOAS e RMV, agrupados na fonte.'),(72,'Abono salarial e seguro-desemprego','Soma dos dois benefícios, conforme rubrica do RTN.'),(85,'Fundeb — complementação da União','Somente a complementação federal; não é todo o financiamento do Fundeb.'),(64,'Benefícios previdenciários (RGPS)','Benefícios previdenciários urbanos e rurais, incluindo sentenças e precatórios; não é toda a Previdência pública.'),(175,'Minha Casa Minha Vida — despesa no RTN','Rubrica orçamentária informada no RTN; não equivale ao total de financiamentos habitacionais ou de recursos do FGTS.')]
renuncia=next(x['nominal'] for x in a['anos'] if x['ano']==2023)
comparadores=[]
for row,label,note in specs:
 value=s.cell(row,col).value*1e6
 assert abs(sum(m.cell(row,k).value or 0 for k in months)*1e6-value)<.01
 comparadores.append(dict(nome=label,valor=value,rotulo_fonte=s.cell(row,1).value,celula=s.cell(row,col).coordinate,aba='2.2',escopo=note,razao=renuncia/value,percentual=renuncia/value*100))
# Reconciliação da despesa total com as quatro rubricas exaustivas, sem somar subitens.
total_despesa=s.cell(63,col).value*1e6
component_rows=[]
for row in range(64,155):
 label=str(s.cell(row,1).value or '').strip()
 if label.startswith(('4.1 ','4.2 ','4.3 ','4.4 ')):component_rows.append(row)
assert len(component_rows)==4,component_rows
assert abs(sum(s.cell(row,col).value for row in component_rows)*1e6-total_despesa)<.01
out=dict(base=a['base'],itens=items,regras_tema=[dict(mecanismo=reg,tema=tema) for reg,tema in sorted(mapping.items())],custo=dict(ano=2023,renuncia=renuncia,despesa_primaria=total_despesa,comparadores=comparadores,url=URL,pdf=PDF,publicacao='2024-01-29',consulta='2026-09-18',metodo='Pagamento efetivo, RTN, tabela 2.2, valores correntes em R$ milhões convertidos para reais.'))
(ROOT/'artifact/composicao-custo.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
(Q/'validacao.json').write_text(json.dumps(dict(composicao=checks,despesa_total=total_despesa,rubricas_exaustivas=component_rows,comparadores= comparadores,soma_mensal_confere=True,arquivos=[dict(arquivo=p.name,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(F.glob('*'))]),ensure_ascii=False,indent=2)+'\n')
(Q/'temas.json').write_text(json.dumps(out['regras_tema'],ensure_ascii=False,indent=2)+'\n')
print('Composição:',len(items),'itens; total 2023:',renuncia)
for r in comparadores:print(r['nome'],r['valor'],r['razao'])
