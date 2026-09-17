# Apresentação — fontes, cálculo e validação

Implementação em 17/09/2026. Pedido: primeira aba explicativa com evolução anual e composição por tipo, em preços de 2024. Referência operacional escolhida: dezembro/2024, indicada nos gráficos e na metodologia. Snapshot fiscal preservado, arquivos atualizados em 05/12/2024 e extraídos em agosto/2026; nenhuma atualização silenciosa da base fiscal.

## Fontes e conceitos

- Originais: https://portaldatransparencia.gov.br/download-de-dados/renuncias
- Dicionário: https://portaldatransparencia.gov.br/dicionario-de-dados/renuncias
- Cobertura: https://portaldatransparencia.gov.br/entenda-a-gestao-publica/renuncias-fiscais
- LRF, art. 14: https://www.planalto.gov.br/ccivil_03/leis/lcp/lcp101.htm#art14
- Exemplo histórico, não data inaugural universal: Decreto-Lei 288/1967, https://www.planalto.gov.br/ccivil_03/decreto-lei/del0288.htm
- IPCA: SIDRA 1737, variável 2266; boletim oficial https://ftp.ibge.gov.br/Precos_Indices_de_Precos_ao_Consumidor/IPCA/Fasciculo_Indicadores_IBGE/2024/ipca-inpc_202412caderno.pdf, página 18. PDF arquivado e hash no JSON de saída. A API SIDRA devolveu HTTP 403 nesta consulta; usamos o boletim primário, sem estimar índices ausentes.

Dicionário e documentação da base já auditados em qa/2026-09-17/reconhecimento.md; dicionário e download reabertos nesta execução. O texto de cobertura reaproveita a documentação arquivada, pois a página explicativa respondeu 405 na ferramenta web. O ano é o fato gerador, segundo a explicação oficial; o dicionário tem descrição imprecisa sobre ano da declaração. Cadastro/habilitação não é renúncia usufruída. Os tipos usados são os três rótulos abreviados de dim_item.tipo_curto, preservando todos os registros do banco.

## Cálculo

`real_ano = nominal_ano × índice_dez2024 / média_índices_mensais_ano`.
Índice dezembro/2024 = 7100,50 (dezembro/1993 = 100), extraído por script da tabela IPCA do PDF. Médias de 2020–2024 conferidas contra os 12 índices do mesmo boletim; anos anteriores mantêm a série SIDRA já validada do pipeline. Não usamos IPCA-15, inflação anual arredondada, nem corrigimos novamente valores já reais.

O exportador 11_export_apresentacao.py consulta mart_ano e fato_item_ano + dim_item no DuckDB. Corrige cada ano antes de acumular por tipo. Totais dos tipos reconciliados com mart_ano em cada ano (tolerância numérica de R$ 0,05, pois o banco usa DOUBLE), e soma real dos tipos reconciliada com soma da série. O detalhe da auditoria anterior reconciliou os brutos em centavos.

Acumulado dos dois gráficos: 2015–2024, com 2024 parcial, sem filtros do dashboard. 2024 inclui importações do primeiro semestre e não inclui IRPJ/CSLL do ano. Não comparar essa barra como queda anual. As participações dos tipos usam o mesmo total corrigido, não total nominal. Cada barra horizontal parte de zero; a maior define a escala comum.

## Comparação com o restante do site

- Apresentação: base dezembro/2024, índice 7100,50.
- Resumo: nominal por padrão; Real usa média de janeiro–dezembro do ano selecionado, inicialmente 2023. Selecionar 2024 significa média de 2024, não dezembro/2024. Rótulos agora explicitam isso.
- Ranking principal: nominal de 2015–2023, sem deflação. A coluna 2023 é o período, não uma conversão do acumulado para preços de 2023.
- Detalhe da empresa: nominal por padrão; opção Real em média janeiro–dezembro/2023; inclui 2024 parcial.
- % PIB: renúncia nominal / PIB nominal do mesmo ano, sem correção isolada do numerador.

Mantendo o recorte e o período, dezembro/2024 supera a base média/2023 em 6,595707948% e a base média/2024 em 2,134998581%. Isso é diferença de referência monetária, não erro de soma. Não uniformizamos as bases das abas sem pedido; explicitamos a diferença. O recorte temporal também difere: ranking 2015–2023 versus apresentação/detalhe 2015–2024 parcial.

O payload do explorador arredonda valores para reais inteiros. Ao confrontar o cubo AGG com os novos totais do banco, a maior diferença nominal anual é R$ 18,11, documentada em interface.json. Não confundimos esse arredondamento com diferença de deflator.

## Suposições e limites

A média anual aproxima a distribuição temporal dos valores anuais. Também foi mantida para 2024, cuja cobertura é parcial; isso é explicitado na página. Sem os valores mensais, não é possível corrigir cada operação no mês exato. Concentração dos valores em meses específicos pode mudar o resultado da correção. A verificação exigiria microdados mensais e os índices dos meses correspondentes.

Os registros de origem, inclusive negativos, repetições preservadas na auditoria anterior e identificação inválida, não foram descartados. A reconciliação não confirma a ausência de erros na fonte. Os conceitos não autorizam generalizar este total para todas as renúncias brasileiras, nem inferir que benefícios históricos continuam vigentes. O IPCA mede inflação ao consumidor, não eficácia dos incentivos.

## Interface

JavaScript validado com node --check. Navegador: aba inicial, dez anos, três tipos, indicação de parcial, independência dos filtros, navegação entre três abas, preservação de ranking nominal, detalhe em média/2023, todos os 62 estabelecimentos da Petrobras e ausência de erros JS. Capturas em 1300 e 420 px. Gráfico anual com rolagem horizontal em telas estreitas para manter os anos legíveis.

Reprodução: `python3 renuncias-fiscais/scripts/11_export_apresentacao.py` e `python3 renuncias-fiscais/scripts/05_build_artifact.py`.
