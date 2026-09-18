# Uniformização dos preços e revisão de rótulos — 18/09/2026

Título: Benefícios tributários por beneficiário. A interface descreve a unidade como beneficiários agrupados por raiz do CNPJ. A metodologia preserva a explicação de que esse agrupamento não identifica todo o grupo econômico.

Todos os valores reais usam o número-índice do IPCA de agosto/2026 (7633,23), dividido pela média dos números-índices dos meses cobertos na origem: janeiro–dezembro de 2015–2023 e janeiro–junho de 2024. O detalhe não aceita mais uma referência antiga por configuração salva no navegador. Os valores nominais continuam disponíveis.

## Conferência

`verificar_interface.py` verifica no Chromium os dez anos contra os valores de referência, abertura do detalhe da Petrobras, alternância real/nominal, título e rótulos, e navegação pelas cinco abas. Resultados em `validacao.json` e captura do detalhe em `detalhe-real.png`.

Na Petrobras, o acumulado corrigido é R$ 171,35 bilhões, contra R$ 122,43 bilhões nominais. A diferença entre o cálculo no navegador e a referência detalhada é de aproximadamente R$ 0,16, decorrente do arredondamento do payload já existente; não muda o valor apresentado. Os dez totais anuais corrigidos pela função da interface são iguais aos da apresentação na precisão numérica utilizada.

Reexecutada também a auditoria dos 20 CSVs monetários e das 251.331 combinações de CNPJ/ano, com resultados em `conferencia-brutos.json`. Totais anuais, composição, setores e concentração conferem. O índice e as médias históricas foram consultados e conferidos no IBGE na revisão anterior desta mesma data.

## Suposições e limites

A média dos índices aproxima o fluxo anual sem informação mensal. A uniformização muda a referência de apresentação; não modifica o tratamento dos registros fiscais. Permanecem a cobertura parcial de 2024, repetições preservadas, negativos e identificador inválido. Os demais problemas de contagem e classificação registrados na revisão não estão entre as três correções solicitadas nesta rodada.
