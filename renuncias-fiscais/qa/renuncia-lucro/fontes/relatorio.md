# Auditoria da comparação com EBITDA de Carabetta

Escopo: Yahoo Finance/yfinance e código original; nenhum dado CVM utilizado. Consulta em 17/09/2026.

Reproduzidos 16 dos 17 EBITDAs na precisão de uma casa decimal em bilhões; 1 divergência. Também reproduzidos os vinte lugares do ranking acumulado por razão social, os números de CNPJs e os valores fiscais exibidos, com os CSVs locais e o deflator do autor.

## Seleção e períodos

O SQL agrupa por Razão Social, ordena pela soma corrigida de 2015–2024 e limita a vinte. Mantém todos os estabelecimentos com a mesma razão social; não agrupa por raiz e não comprova grupo econômico. O Ministério da Saúde é excluído da comparação financeira por regra explícita. Ventura não tem ticker configurado e GOLL4.SA retorna DRE vazia. Logo: vinte selecionados, dezenove linhas financeiras e dezessete EBITDAs.

Ren./EBITDA = renúncia somente de 2023, corrigida pelo IPCA, dividida pelo EBITDA anual convertido com câmbio fixo. Acum./VM é outra métrica: renúncia acumulada de 2015–2024 dividida pelo valor de mercado obtido na consulta.

Escolha da DRE: primeira coluna cujo ano final é 2023; se ausente, 2022; se ambas ausentes, primeira coluna disponível. Essa substituição não é exibida no HTML. Na reconsulta, todos os dezessete valores vêm de coluna com ano final 2023: dezesseis terminam em dezembro e MITSY termina em março. Não foi necessário fallback de ano. O campo foi EBITDA em todos; Normalized EBITDA é apenas alternativa prevista no código.

## Origem e reprodução de cada linha

|Posição|Beneficiário|Ticker definido pelo autor|Escopo do mapeamento|Data final da DRE|Valor original Yahoo|Moeda adotada pelo código|EBITDA HTML (R$ bi)|Reprodução (R$ bi)|Resultado|
|---|---|---|---|---|---:|---|---:|---:|---|
|1|Petrobras|PETR4.SA|entidade|2023-12-31|52.292.000.000|USD|253.8|253,6|diverge|
|2|GE Celma|GE|proxy|2023-12-31|12.649.000.000|USD|61.3|61,3|coincide|
|3|Vale|VALE3.SA|entidade|2023-12-31|15.590.000.000|USD|75.6|75,6|coincide|
|4|Samsung Amazônia|005930.KS|proxy|2023-12-31|50.603.077.000.000|KRW|189.8|189,8|coincide|
|5|Embraer|EMBJ3.SA|entidade|2023-12-31|598.200.000|USD|2.9|2,9|coincide|
|6|LATAM (TAM)|LTM|proxy|2023-12-31|1.279.379.000|USD|6.2|6,2|coincide|
|7|Stellantis Brasil|STLA|proxy|2023-12-31|31.297.000.000|EUR|166.5|166,5|coincide|
|8|Modec|MITSY|proxy|2023-03-31|1.782.566.000.000|JPY|60.6|60,6|coincide|
|9|GM Brasil|GM|proxy|2023-12-31|23.202.000.000|USD|112.5|112,5|coincide|
|10|CNH Industrial|CNH|proxy|2023-12-31|4.612.000.000|USD|22.4|22,4|coincide|
|11|Caterpillar Brasil|CAT|proxy|2023-12-31|15.705.000.000|USD|76.2|76,2|coincide|
|12|Renault Brasil|RNO.PA|proxy|2023-12-31|6.394.000.000|EUR|34.0|34,0|coincide|
|13|Yara Brasil|YAR.OL|proxy|2023-12-31|1.531.000.000|USD|7.4|7,4|coincide|
|14|Syngenta Brasil|FMC|proxy|2023-12-31|721.700.000|USD|3.5|3,5|coincide|
|15|Ministério da Saúde|—|sem ticker|—|—|—|—|—|excluído por código|
|16|Ventura Petróleo|—|sem ticker|—|—|—|—|—|sem ticker|
|17|LG Brasil|066570.KS|proxy|2023-12-31|5.767.150.000.000|KRW|21.6|21,6|coincide|
|18|Volkswagen Brasil|VOW3.DE|proxy|2023-12-31|54.305.000.000|EUR|288.9|288,9|coincide|
|19|Azul|AZUL|entidade|2023-12-31|4.618.956.000|BRL|4.6|4,6|coincide|
|20|Gol|GOLL4.SA|entidade|—|—|—|—|—|sem demonstração ou falha de consulta|

## Conversões e limites da reprodução

Taxas fixas usadas, não baixadas do BCB pelo código: USD × 4,85; EUR × 5,32; KRW × 0,00375; JPY × 0,034; BRL × 1. A atribuição “câmbio médio de dezembro de 2023 / BCB” é um comentário do autor; esta auditoria reproduz as taxas, não certifica essa atribuição.

Para PETR4.SA, VALE3.SA e EMBJ3.SA, financialCurrency retornou BRL, mas a regra valor de mercado/receita > 4 trocou a moeda para USD antes de converter. O valor de mercado é atual, embora a receita seja histórica. Essa é uma heurística do autor, não uma validação contábil da moeda. O CSV preserva as duas moedas e os metadados preservam o valor de mercado.

Petrobras: o Yahoo retornou EBITDA bruto 52.292.000.000; multiplicado pela taxa do código resulta em R$ 253,6162 bi, contra R$ 253,8 bi no HTML. Sem o snapshot Yahoo da geração original, a causa da diferença não está provada.

O numerador 2023 é multiplicado por 1,132563902 (+13,26%). O EBITDA não recebe IPCA. Portanto, as razões têm bases monetárias diferentes; em relação à mesma divisão sem essa correção só no numerador, ficam 13,26% maiores.

O rótulo da base é jul/2026, mas ipca.py só contém taxas mensais até junho/2026, identifica junho como IPCA-15 e ignora mês ausente. O algoritmo não aplica taxa de julho. Não validamos as taxas do dicionário contra o IBGE; a inconsistência entre rótulo e execução está no código.

## Quem está fora das vinte razões sociais

As treze proxies são emissores externos à entidade brasileira selecionada. Não são treze beneficiários adicionais. O vínculo é uma lista manual de padrões de nome: primeiro padrão encontrado vence, sem QSA/CNPJ/tabela de participação societária. GE Celma→GE; Samsung→005930.KS; TAM→LTM; Stellantis→STLA; Modec→MITSY; GM→GM; CNH→CNH; Caterpillar→CAT; Renault→RNO.PA; Yara→YAR.OL; Syngenta→FMC; LG→066570.KS; Volkswagen→VOW3.DE. A alegação societária Modec/Mitsui é nota do autor, não comprovada nesta auditoria. FMC é explicitamente aproximação setorial para Syngenta, não sua própria demonstração.

O mapa também tem Volvo, TAP Manutenção, Brasfels e Scania. Essas regras extras não são acionadas porque tais razões sociais não estão no top vinte reproduzido. Não contribuem valores para a tabela examinada.

## Proveniência

Código: https://github.com/JoaoCarabetta/data-analysis/tree/66d9cbb7967a4eb01f3e8570d299ff6e917dd60a/projects/2026-09-11-renuncias-fiscais (acesso depende de permissão). Copiado localmente em codigo-origem/. financeiro.py define tickers, moedas, fallbacks e cálculos; gerar_relatorio_site.py define o SQL e as colunas; ipca.py define o deflator.

O HTML arquivado nesse projeto e a cópia do site público têm o mesmo SHA-256: 8ace9fbfd05913f5cff9a635d20c7dc3eb58c38910ed425c90d9281079504409. O código foi arquivado em setembro e a publicação data de julho; a igualdade dos HTMLs e a reprodução dos valores dão evidência, mas não substituem um snapshot histórico das consultas Yahoo.

Reprodução: script 08 consulta Yahoo e executa a função original sobre os snapshots capturados; script 09 reconstitui o ranking fiscal e gera este relatório. Dependências usadas: yfinance 1.7.0, pandas, beautifulsoup4. Fontes brutas Yahoo em yahoo/<ticker>/. A responsabilidade pelos valores originais é das fontes; conferir reprodução não confirma adequação econômica do cruzamento.
