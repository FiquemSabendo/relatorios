# Renúncias fiscais federais, 2015–2024

**Publicado:** <https://relatorios.fiquemsabendo.com.br/renuncias-fiscais/>

Pipeline reprodutível que baixa os microdados de **Renúncias Fiscais** do Portal da
Transparência, consolida em um banco DuckDB e gera uma página HTML autocontida
(`../docs/renuncias-fiscais/index.html`, servida pelo GitHub Pages; cópia em `artifact/renuncias.html` para o
artefato do claude.ai; ~9 MB), na identidade visual da Fiquem Sabendo, com seis abas:

- **Apresentação** — série anual e composição por tributo, corrigidas pelo IPCA.
- **Metodologia** — cobertura, fontes, agrupamentos e correção monetária.
- **Inconsistências** — evidências nos dados brutos, arquivos para conferência e perguntas propostas ao Ministério da Fazenda.
- **Maiores Beneficiários** — concentração, maiores beneficiários e setores; tabela de todos os setores em todos os anos, de 2015 a 2024 (parcial).
- **Ranking de beneficiários** — agrupamento por raiz do CNPJ, com busca e detalhes dos estabelecimentos, valores anuais e fundamentos legais.

O banco guarda mais do que o artefato mostra: concentração por setor, matriz setor ×
mecanismo e métricas de outlier estão em `mart_setor_regime` e `mart_grupo_ano`.

## Como rodar

A partir desta pasta (`renuncias-fiscais/`):

```bash
bash   scripts/01_download.sh      # baixa e extrai os ZIPs de 2015 a 2024
python3 scripts/02_macro.py        # IPCA e PIB via API do SIDRA/IBGE
duckdb renuncias.duckdb < scripts/03_build_db.sql
python3 scripts/04_export_payload.py   # artifact/payload.json
python3 scripts/12_atualizar_referencia_ipca.py # consulta último IPCA mensal oficial
python3 scripts/11_export_apresentacao.py # apresentação e índices dos períodos cobertos
python3 scripts/05_build_artifact.py   # artifact/renuncias.html e ../docs/renuncias-fiscais/index.html
```

O GitHub Pages serve a pasta `docs/` da raiz do repositório a partir da branch `main`;
publicar é fazer commit do arquivo gerado.

Requisitos: `curl`, `unzip`, `duckdb` (CLI) e os módulos Python `duckdb`, `pypdf` e `requests`. Sem pandas.

Para atualizar quando o Portal publicar um novo ano: apague `data/raw/zips/`, rode tudo
de novo e ajuste `ANO_PARCIAL` em `scripts/04_export_payload.py` se o ano mais recente
ainda estiver incompleto.

## Fonte

| | |
|---|---|
| Dados | [Portal da Transparência — Renúncias Fiscais](https://portaldatransparencia.gov.br/download-de-dados/renuncias) |
| URL direta | `https://dadosabertos-download.cgu.gov.br/PortalDaTransparencia/saida/renuncias/{ANO}_RenunciasFiscais.zip` |
| Anos | 2015 a 2024 (anteriores a 2015 retornam 403) |
| Formato | CSV `;`, latin-1, CRLF, decimal com vírgula |
| IPCA | SIDRA tabela 1737, variável 2266 (número-índice mensal) |
| PIB | SIDRA tabela 1846, variável 585, categoria 90707 (trimestral, preços correntes) |

Cada ZIP traz quatro CSVs. O pipeline usa dois:

- `{ano}_RenúnciasFiscais.csv` — uma linha por CNPJ × benefício × fundamento legal;
- `{ano}_RenúnciasFiscaisPorBeneficiário.csv` — o total por CNPJ.

`EmpresasHabilitadas` e `EmpresasImunesOuIsentas` ficam em disco mas não entram no banco:
habilitação e imunidade não são valor de renúncia.

## O banco

`renuncias.duckdb` (~90 MB) tem três camadas:

- **staging** — `stg_beneficiario`, `stg_detalhe` (leitura direta dos CSVs);
- **dimensões** — `dim_estab` (77.523 CNPJs), `dim_grupo` (69.463 raízes de CNPJ),
  `dim_cnae` (com seção CNAE 2.0 derivada da divisão), `dim_item` (301 pares benefício
  fiscal × fundamento legal, com o mecanismo classificado);
- **fatos e marts** — `fato_empresa_ano` (251.331 linhas), `fato_item_ano` (711.116),
  `mart_ano`, `mart_setor_ano`, `mart_uf_ano`, `mart_item_ano`, `mart_regime_ano`,
  `mart_setor_regime` e `mart_grupo_ano`, este último já com as métricas de outlier
  (z robusto contra a própria história e contra o setor, variação anual, participação no
  ano, estreia).

### Mecanismo jurídico

O campo `Fundamento Legal` do arquivo detalhado traz **162 dispositivos distintos** — é o
que identifica de onde vem a renúncia. Para o IRPJ/CSLL declarado, o benefício já nomeia o
programa (PAT, Prouni, Perse, Sudam/Sudene, Rouanet…); para a renúncia de importação, o
mecanismo só aparece no fundamento (Repetro, Recof, Drawback, Zona Franca de Manaus,
admissão temporária, entreposto aduaneiro…).

A macro `regime_de(tipo, benefício, fundamento)` em `03_build_db.sql` agrupa esses 162
dispositivos em **40 mecanismos** por regra explícita sobre o texto, com balde residual
nomeado — 0,5% do valor cai em "Outros fundamentos de importação". O fundamento original
nunca é descartado: aparece ao lado em todas as telas. Maiores mecanismos:

| Mecanismo | R$ bi | Grupos |
|---|---|---|
| Regimes aduaneiros especiais (PIS/Cofins) | 257,7 | 16.273 |
| Sudam/Sudene | 126,5 | 2.163 |
| Zona Franca de Manaus | 117,9 | 1.567 |
| Desoneração de alimentos e insumos agrícolas | 116,5 | 1.820 |
| Repetro (petróleo e gás) | 107,2 | 201 |
| Recof (entreposto industrial) | 88,2 | 58 |

O maior deles é um catch-all da própria origem: "Bens Submetidos Aos Regimes Aduaneiros
Especiais (Lei 10865/04 - Art. 14, Caput)" é o guarda-chuva de PIS/Cofins-importação para
drawback, admissão temporária, entreposto e afins, sem abertura na fonte.

Consulta de exemplo:

```sql
SELECT nome_grupo, round(valor_total/1e9, 2) AS bi, n_estab
FROM dim_grupo ORDER BY valor_total DESC LIMIT 10;
```

## Conferências

O total por ano bate exatamente entre os dois arquivos de origem:

| Ano | R$ bi | | Ano | R$ bi |
|---|---|---|---|---|
| 2015 | 75,13 | | 2020 | 159,36 |
| 2016 | 78,29 | | 2021 | 204,74 |
| 2017 | 70,59 | | 2022 | 194,70 |
| 2018 | 100,23 | | 2023 | 179,36 |
| 2019 | 119,44 | | 2024 | 70,65 *(parcial)* |

Amostras conferidas contra o CSV bruto: VALE S.A. (33592510000154) em 2023 =
R$ 4.996.764.547,33; GE CELMA (33435231000187) em 2019 = R$ 3.349.826.323,69.

## Ressalvas

- **2024 é parcial.** O arquivo do Portal foi atualizado pela última vez em 05/12/2024 e
  traz R$ 70,6 bi e 11.732 CNPJs, contra R$ 179,4 bi e 39.723 em 2023. O artefato deixa
  2024 fora por padrão.
- **13,7% do valor não tem CNAE** na origem (código `00000`). Vira a categoria
  "Sem informação", não é descartado.
- **Grupo econômico é aproximado pela raiz do CNPJ.** Une matriz e filiais, mas não capta
  controle societário entre CNPJs de raízes diferentes.
- A base traz um registro-sentinela da Receita (`CNPJ -3`, razão social "Inválido",
  R$ 127.219,00 em 2017). Ele é mantido para que os totais fechem.
- O recorte é federal: não cobre ICMS, ISS, Simples Nacional nem renúncias de pessoa física.

## O artefato

`artifact/renuncias.html` é autocontido (~9,0 MB) porque a CSP do host bloqueia requisições
externas. Os microdados vão embutidos como TSV comprimido em gzip e codificado em base64,
descompactados no navegador com `DecompressionStream` — sem biblioteca externa, inclusive
para os gráficos, todos em SVG/Canvas desenhados à mão. São quatro blobs:

| Blob | Conteúdo | Linhas | gzip |
|---|---|---|---|
| `DIM` | cadastro por CNPJ | 77.523 | 1,84 MB |
| `FATO` | total por CNPJ e ano | 251.331 | 0,95 MB |
| `ITEM` | CNPJ × ano × benefício × fundamento legal | 711.116 | 3,34 MB |
| `AGG` | cubo exato ano × item × seção × UF | 67.861 | 0,42 MB |

A abertura por fundamento legal cobre **todos** os 77.523 CNPJs, não uma amostra. O
carregamento no navegador leva cerca de 0,8 s depois do download.

`artifact/template.html` é a fonte editável do explorador; `05_build_artifact.py` injeta o
payload e as fontes e grava `artifact/renuncias.html` e `../docs/renuncias-fiscais/index.html`. Edite o template,
nunca os arquivos gerados.

## Filtros e detalhe das empresas

Os controles de medida, seção CNAE e inclusão de 2024 aparecem somente no dashboard.
O ranking usa valores nominais de 2015–2023 e não herda os filtros do dashboard.
Ao voltar ao dashboard, as seleções anteriores são preservadas.

Ao abrir uma empresa no ranking, o detalhe inclui sempre 2024, identificado como parcial,
e oferece as opções Nominal e Real (IPCA, R$ de 2023). Essa opção afeta os valores,
gráficos e tabelas do detalhe, sem alterar a ordenação ou os valores do ranking.
O acumulado do detalhe inclui 2024 e, portanto, tem período diferente do ranking.
As verificações de interface estão em `qa/filtros-ranking/`.

## Setor e atividade

O ranking também oferece uma classificação editorial por setores, como Automotivo, Aviação e Farmacêutico,
com a atividade específica no detalhe da empresa,
com origem e evidência acessíveis ao abrir a empresa. Regras, critérios de preenchimento
de lacunas e limites estão em [METODOLOGIA-SETORES.md](METODOLOGIA-SETORES.md).
Para atualizar apenas a classificação, use `python3 scripts/04_export_payload.py --somente-setores`
e depois regenere o HTML com `05_build_artifact.py`.

## Apresentação e bases de preços

A primeira aba explica a base e apresenta a série anual e a composição por tributo em reais de
agosto/2026 (último IPCA mensal disponível na consulta de 17/09/2026). O gerador `scripts/11_export_apresentacao.py` consulta o banco, extrai os índices
de origem do boletim oficial arquivado e lê a referência em `data/macro/referencia-ipca.json`; produz `artifact/apresentacao.json`, incorporado
ao HTML por `05_build_artifact.py`. Fontes, fórmula, conciliação, diferenças para
o ranking e limitações estão em [qa/apresentacao/metodologia.md](qa/apresentacao/metodologia.md).

No detalhe do ranking, preços reais usam a média janeiro–dezembro de 2023. O ranking principal permanece nominal. Esses rótulos são
explícitos na interface; a referência mais recente não foi aplicada às demais abas.

### Cobertura temporal do deflator

Regra vigente em todas as visualizações reais: média de janeiro–dezembro na origem para
2015–2023; média de janeiro–junho para 2024. A cobertura fica em
`data/macro/cobertura-deflacao.json`; o exportador 11 gera os índices de origem e o
conversor comum do site os aplica no detalhe do ranking. A referência
monetária de apresentação é independente dessa cobertura. Não substituir a média
anual de referência em `data/macro/ipca.csv` pela média semestral.

Depois de alterar cobertura ou dados fiscais: executar `11_export_apresentacao.py` antes
de `05_build_artifact.py`. A construção do HTML verifica a compatibilidade da cobertura
com o JSON gerado. Revalidar a configuração se o snapshot fiscal for atualizado.

Para atualizar a referência de “dinheiro de hoje”, rodar `12_atualizar_referencia_ipca.py`,
`11_export_apresentacao.py` e `05_build_artifact.py`, nessa ordem. A resposta oficial fica
arquivada em `qa/referencia-ipca/`; o build não consulta a internet nem muda a referência
silenciosamente. A API alternativa oficial de agregados do IBGE fornece SIDRA 1737/2266.

## Abas e maiores beneficiários

Ordem: Apresentação, Metodologia, Inconsistências, Maiores Beneficiários, Ranking de beneficiários e Renúncia vs Lucro.
A Metodologia reúne a descrição da base, as fontes e os critérios em uma aba própria.
Maiores Beneficiários usa o acumulado real de 2015–2024, incluindo 2024 parcial.
Concentração por raiz do CNPJ, sem inferir controlador; inclui empresas e outras pessoas
jurídicas. Os setores são somados por estabelecimento usando a classificação editorial,
em vez de atribuir todo o grupo ao setor do estabelecimento principal. A tabela anual mostra todos os setores nos dez anos, sem gráfico de evolução,
com 2024 identificado como parcial e totais anuais para conferência. Detalhes em `qa/maiores-beneficiarios/metodologia.md`.

## Auditoria de inconsistências

`python3 renuncias-fiscais/scripts/13_export_inconsistencias.py` relê os CSVs monetários originais, reconcilia cada CNPJ/ano e gera `artifact/inconsistencias.json` e os CSVs públicos em `docs/renuncias-fiscais/evidencias/`. Rodar antes do build quando mudar a base. A aba distingue pendências dos registros de limitações documentais e não confirma erros ou irregularidades. Ver `qa/inconsistencias/consistencia.md`.

## Renúncia vs Lucro

A aba reproduz a seleção e as aproximações financeiras autorizadas do Carabetta, com vinte beneficiários e dezoito EBITDAs. Fonte versionada: `qa/renuncia-lucro/fontes/`, incluindo a tabela em Markdown e snapshots Yahoo de 17/09/2026. `scripts/14_export_renuncia_lucro.py` gera `artifact/renuncia-lucro.json` e o CSV público. Não faz consultas novas. Os percentuais são recalculados com o EBITDA histórico arredondado, salvo Volvo, cujo valor integral foi preservado. A renúncia de 2023 recebe o fator histórico do autor e o EBITDA não: essa reprodução é uma exceção explícita às bases de preços das outras abas e não mede parcela do lucro causada pelo incentivo. Ver metodologia na própria aba e `qa/renuncia-lucro/consistencia.md`.
