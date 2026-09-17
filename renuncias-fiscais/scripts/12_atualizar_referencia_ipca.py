#!/usr/bin/env python3
"""Consulta o último IPCA mensal oficial; congela referência e proveniência para o build."""
import datetime
import hashlib
import json
from pathlib import Path
import requests
ROOT = Path(__file__).resolve().parents[1]
URL = 'https://servicodados.ibge.gov.br/api/v3/agregados/1737/periodos/-1/variaveis/2266?localidades=N1[all]'
r = requests.get(URL, timeout=60)
r.raise_for_status()
data = r.json()
assert len(data) == 1 and data[0]['id'] == '2266'
series = data[0]['resultados'][0]['series']
assert len(series) == 1 and series[0]['localidade']['id'] == '1'
values = series[0]['serie']
assert len(values) == 1
period, value = next(iter(values.items()))
index = float(value)
today = datetime.date.today()
assert len(period) == 6 and period.isdigit() and 1 <= int(period[4:]) <= 12
assert period <= today.strftime('%Y%m') and index > 0
months = ['janeiro','fevereiro','março','abril','maio','junho','julho','agosto','setembro','outubro','novembro','dezembro']
out = dict(base=f'{months[int(period[4:])-1]} de {period[:4]}',base_mes=f'{period[:4]}-{period[4:]}',
 indice_base=index,indice='IPCA',variavel=data[0]['variavel'],fonte=URL,fonte_periodo=URL.replace('/-1/',f'/{period}/'),
 consultado_em=datetime.datetime.now(datetime.timezone.utc).isoformat(),
 fonte_sha256=hashlib.sha256(r.content).hexdigest(),criterio='Último período disponível do IPCA mensal Brasil, SIDRA 1737, variável 2266; não IPCA-15 nem projeção.')
qa = ROOT/'qa/referencia-ipca';qa.mkdir(exist_ok=True)
(qa/'resposta-ibge.json').write_bytes(r.content)
(ROOT/'data/macro/referencia-ipca.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(out,ensure_ascii=False,indent=2))
