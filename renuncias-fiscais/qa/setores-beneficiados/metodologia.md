# Setores beneficiados — reorganização de 18/09/2026

O gráfico e a tabela anual foram movidos de Maiores Beneficiários para Setores beneficiados. O seletor alterna entre a classificação editorial existente e a seção CNAE do cadastro já utilizado pelo projeto. A unidade de classificação é o estabelecimento; não se atribui o setor principal da raiz a todas as filiais.

A exportação usa `fato_empresa_ano`, `dim_estab` e um LEFT JOIN com `dim_cnae`. Ausência de seção vira “Sem informação”. Preservam-se registros negativos e identificadores inválidos. Período: 2015–2024, com 2024 parcial. Deflação inalterada: IPCA de agosto/2026 dividido pela média anual de 2015–2023 ou pela média jan–jun/2024.

Há 39 categorias editoriais e 19 seções/categorias CNAE presentes no acervo. O gráfico apresenta os dez maiores setores identificados; a tabela inclui todas as categorias. As duas aberturas foram conciliadas com cada total anual: diferenças inferiores a R$ 0,001 decorrentes da soma em ponto flutuante, sem diferença no centavo. Resultados em validacao.json.

Maiores Beneficiários mantém os indicadores de concentração em valores corrigidos e passa a conter o ranking completo nominal, com busca e expansão. A tabela estática de top 20 e a aba Ranking foram removidas. Links antigos #ranking abrem #beneficiarios.

Verificação no navegador: seletor altera gráfico e tabela; busca por raiz retorna Petrobras; expansão mantém rótulos anuais e gráficos lado a lado; todas as abas abrem sem erro JavaScript. Inspeção visual desktop 1300 px e celular 420 px.
