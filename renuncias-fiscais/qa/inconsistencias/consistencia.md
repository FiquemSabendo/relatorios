# Inconsistências — revisão de 17/09/2026

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
