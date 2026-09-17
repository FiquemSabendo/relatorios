#!/usr/bin/env python3
"""Exporta correspondências e cobertura da classificação editorial."""
from pathlib import Path
from collections import Counter,defaultdict
import csv,json,hashlib
import duckdb
from classificacao_setorial import classificar_estabelecimentos,classificar_cnae,ESPECIFICAS,DIVISOES,VERSION
R=Path(__file__).resolve().parents[1];Q=R/'qa/setores-detalhados';Q.mkdir(exist_ok=True,parents=True)
c=duckdb.connect(str(R/'renuncias.duckdb'),read_only=True)
estabs=c.execute('select estab_id,cnpj,razao_social,nome_fantasia,cnae,municipio,uf from dim_estab order by estab_id').fetchall()
rows=classificar_estabelecimentos(estabs);assert len(rows)==len(estabs)==len({r['cnpj'] for r in rows})
assert [r['estab_id'] for r in rows]==list(range(len(rows)))
def save(name,rs):
 with (Q/name).open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=rs[0],lineterminator="\n");w.writeheader();w.writerows(rs)
save('classificacao_por_cnpj.csv',rows)
classes=c.execute('select cnae,descricao,secao_nome from dim_cnae order by cnae').fetchall()
ibge={x['id']:x for x in json.loads((Q/'cnae-ibge.json').read_text())}
correspondencias=[dict(cnae=k,descricao_origem=d,secao=s,setor_detalhado=classificar_cnae(k)[0],regra=classificar_cnae(k)[1],descricao_ibge=ibge.get(k,{}).get('descricao','Não localizado no catálogo consultado')) for k,d,s in classes]
save('dicionario_cnae_setor.csv',correspondencias)
save('regras.csv',[dict(prioridade=5-len(k),prefixo=k,setor=v) for rules in [ESPECIFICAS,DIVISOES] for k,v in sorted(rules.items())])
values=dict(c.execute('select estab_id,sum(cast(valor as decimal(20,2))) from fato_empresa_ano group by 1').fetchall());by=defaultdict(lambda:{'cnpjs':0,'valor':0});methods=defaultdict(lambda:{'cnpjs':0,'valor':0})
for r in rows:
 key=r['setor_detalhado'];v=values[r['estab_id']];by[key]['cnpjs']+=1;by[key]['valor']+=v
 method='cnae' if r['regra'].startswith('cnae_') and key!='Não identificado' else r['regra'].split(':')[0];methods[method]['cnpjs']+=1;methods[method]['valor']+=v
assert sum(x['valor'] for x in by.values())==sum(values.values())
save('cobertura_por_setor.csv',[dict(setor=k,**v) for k,v in sorted(by.items(),key=lambda p:-p[1]['valor'])])
save('cobertura_por_metodo.csv',[dict(metodo=k,**v) for k,v in methods.items()])
# O representante do frontend é escolhido pelo acumulado de todos os anos (inclusive 2024).
roots=defaultdict(list)
for r in rows:roots[r['cnpj'][:8]].append(r)
top=[]
for root,rs in roots.items():
 principal=max(rs,key=lambda r:(values[r['estab_id']],-r['estab_id']));top.append(dict(raiz=root,nome=principal['razao_social'],setor_detalhado=principal['setor_detalhado'],cnae=principal['cnae_original'],metodo=principal['regra'],n_setores_na_raiz=len({x['setor_detalhado'] for x in rs}),valor=sum(values[r['estab_id']] for r in rs)))
save('ranking_setores.csv',sorted(top,key=lambda r:-r['valor']))
summary=dict(versao=VERSION,cnpjs=len(rows),classes=len(classes),setores=len(by),total=str(sum(values.values())),sem_classificacao=by.get('Não identificado'),por_metodo=methods,classes_fora_catalogo=[r['cnae'] for r in correspondencias if r['cnae']!='00000' and r['cnae'] not in ibge])
(Q/'sumario.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2,default=str))
print(json.dumps(summary,ensure_ascii=False,indent=2,default=str))
