#!/usr/bin/env python3
"""Audita os CSVs monetários originais e exporta evidências da aba Inconsistências."""
from pathlib import Path
from collections import defaultdict
from decimal import Decimal
import csv, hashlib, json
R = Path(__file__).resolve().parents[1]
Q = R/'qa'/'inconsistencias'
Q.mkdir(exist_ok=True)
OUT = R.parent/'docs'/'renuncias-fiscais'/'evidencias'
OUT.mkdir(exist_ok=True)

def cents(s): return int(Decimal(s.replace(',', '.'))*100)
def write(name, rows):
    with (OUT/name).open('w', encoding='utf-8-sig', newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

annual=[]; duplicates=[]; negatives=[]; invalid=[]; hashes=[]
for year in range(2015,2025):
    totals=[]; seen=set(); extra=0; negsum=0; missum=0; misn=0; sent=0; sentn=0; n=0
    for suffix in ['RenúnciasFiscais','RenúnciasFiscaisPorBeneficiário']:
        path=R/'data'/'raw'/str(year)/f'{year}_{suffix}.csv'
        hashes.append(dict(arquivo=str(path.relative_to(R)),sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
        sums=defaultdict(int)
        with path.open(encoding='latin-1',newline='') as f:
            for line,row in enumerate(csv.DictReader(f,delimiter=';'),2):
                v=cents(row['Valor Renúncia Fiscal (R$)']);sums[row['CNPJ']]+=v
                if suffix!='RenúnciasFiscais':continue
                n+=1
                evidence={'arquivo':path.name,'linha_csv':line,**row}
                key=tuple(row.values())
                if key in seen:duplicates.append(evidence);extra+=v
                seen.add(key)
                if v<0:negatives.append(evidence);negsum+=v
                if row['CNPJ']=='-3':invalid.append(evidence);sent+=v;sentn+=1
                if row['Código CNAE'].strip() in ('','00000'):
                    misn+=1;missum+=v
        totals.append(dict(sums))
    assert totals[0]==totals[1],f'Divergência detalhe/totalizador em {year}'
    annual.append(dict(ano=year,linhas=n,total_centavos=sum(totals[0].values()),duplicatas_centavos=extra,negativos_centavos=negsum,cnae_ausente_linhas=misn,cnae_ausente_centavos=missum,sentinela_linhas=sentn,sentinela_centavos=sent))
write('repeticoes.csv',duplicates);write('negativos.csv',negatives);write('identificador-invalido.csv',invalid);write('auditoria-anual.csv',annual);write('arquivos-sha256.csv',hashes)
result=dict(anos=annual,repeticoes=len(duplicates),negativos=len(negatives),sentinela=len(invalid),duplicatas_centavos=sum(r['duplicatas_centavos'] for r in annual),negativos_centavos=sum(r['negativos_centavos'] for r in annual),sentinela_centavos=sum(r['sentinela_centavos'] for r in annual),cnae_ausente_linhas=sum(r['cnae_ausente_linhas'] for r in annual),cnae_ausente_centavos=sum(r['cnae_ausente_centavos'] for r in annual),total_centavos=sum(r['total_centavos'] for r in annual))
# Revalida o principal achado da auditoria anterior, sem depender de seus arquivos locais.
assert result['repeticoes']==307 and result['duplicatas_centavos']==23805764849
(R/'artifact'/'inconsistencias.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
(Q/'consistencia.md').write_text('''# Inconsistências — revisão de 17/09/2026

Fonte: CSVs originais locais de 2015–2024, extraídos em 21/08/2026; atualização indicada no manifesto: 05/12/2024. Nenhum dado fiscal foi alterado. Valores nominais em centavos, sem deflação.

Reprodução: `python3 renuncias-fiscais/scripts/13_export_inconsistencias.py` e `python3 renuncias-fiscais/scripts/05_build_artifact.py`.

O exportador relê os vinte CSVs monetários e exige igualdade do detalhe com o totalizador para cada CNPJ/ano. Identifica repetições pela igualdade de todas as colunas, contando apenas ocorrências além da primeira, e exporta os números de linha (cabeçalho = linha 1). Valores negativos e identificador -3 são listados integralmente. CNAE ausente corresponde ao código vazio ou 00000 no próprio detalhe, sem aplicar o cadastro retrospectivo do site. Seus montantes não equivalem à categoria editorial Não identificado.

Evidências públicas: `docs/renuncias-fiscais/evidencias/`; hashes dos vinte arquivos, resumos anuais e registros de cada caso. Não somar os montantes das inconsistências: os conjuntos podem se sobrepor.

## Suposições e riscos

- Repetições preservadas: a hipótese de duplicação indevida não foi confirmada. Se confirmada, sua remoção reduziria o acumulado pelo montante excedente calculado; solicitar chave e regra da fonte.
- Negativos preservados: não assumimos estorno, erro ou devolução; pedir natureza e vínculo com os registros originais. O tratamento pode alterar saldos.
- Código -3 preservado nos totais: não atribuído a uma empresa. Esclarecer significado e identificadores substitutos; sua identificação afeta atribuição e concentração.
- CNAE ausente impede classificação direta. Solicitar cadastro e data de referência; correções podem redistribuir setores sem mudar o total.
- Ano-calendário interpretado como fato gerador, seguindo a página explicativa; divergência com o dicionário permanece em 17/09/2026. Se a convenção variar entre tipos, comparações anuais precisam ser revistas.
- Cobertura parcial de 2024 é documentada, não erro comprovado. Pedir cronograma e matriz de cobertura; dados adicionais mudariam as comparações, sem autorizar extrapolação automática.

Documentação relida em 17/09/2026: https://portaldatransparencia.gov.br/dicionario-de-dados/renuncias e https://portaldatransparencia.gov.br/entenda-a-gestao-publica/renuncias-fiscais . Perguntas são propostas, não pedidos enviados nem respostas recebidas.
''')
print(json.dumps(result,ensure_ascii=False))
