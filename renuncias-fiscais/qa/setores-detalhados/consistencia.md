# Consistência

77523 CNPJs de entrada e saída; nenhuma exclusão. Todas as classes não nulas foram encontradas no catálogo IBGE consultado. Soma da classificação fecha ao centavo com os fatos: R$ 1252499219562.54.

39 rótulos, incluindo Não identificado. Permanecem sem classificação 7688 CNPJs, com 7.52% do valor de 2015–2024 (inclui ano parcial). O resíduo excede 5% por ausência de CNAE/evidência, não por classes conhecidas sem regra; exige pesquisa cadastral complementar se for necessário reduzi-lo.

Todos os campos anteriores do payload são idênticos aos anteriores à alteração, incluindo os quatro blobs, indicadores macro e cadastro. Apenas classificacao_setorial foi adicionada. Uma reexportação integral de diagnóstico apresentou diferenças de R$ 1 em doze células do cubo por arredondamento de somas float; ela foi descartada. A atualização final usa --somente-setores e conserva todos os números originais.

Versão 2026-09-17.2: setores amplos substituem as atividades na coluna do ranking. Conferida igualdade de cada atividade, método, fonte e evidência com a versão anterior; nenhuma nova inferência foi introduzida. Dados fiscais e demais campos do payload permanecem idênticos. Correspondência e contagens em migracao_setores.csv.
