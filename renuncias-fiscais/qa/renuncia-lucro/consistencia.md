# Renúncia vs Lucro — comparação histórica autorizada

## Objeto e fontes

Publicação da tabela de vinte linhas solicitada pelo usuário, preservando o método e os EBITDAs históricos de Carabetta. Fonte imediata: `fontes/tabela_financeira_20.md` e CSV correspondente. A auditoria, reprodução fiscal e consultas Yahoo/yfinance de 17/09/2026 estão em `fontes/`. Não houve nova coleta financeira, uso de CVM ou substituição automática por valores de reconsulta.

Seleção: razões sociais ordenadas pelo acumulado corrigido de 2015–2024, exclusão do Ministério da Saúde e acréscimo de Volvo Brasil (posição fiscal 21). Não equivale ao ranking por raiz nem aos vinte maiores apenas de 2023. São vinte linhas e dezoito denominadores disponíveis.

## Reprodução

Da raiz do repositório:

```bash
python3 renuncias-fiscais/scripts/14_export_renuncia_lucro.py
python3 renuncias-fiscais/scripts/05_build_artifact.py
```

Exportação: `artifact/renuncia-lucro.json` e `docs/renuncias-fiscais/evidencias/renuncia-lucro.csv`. Todo número do gráfico e das tabelas vem desse produto. EBITDA histórico extraído do texto do CSV, não transcrito à mão. Volvo usa o valor integral da consulta adicional. Denominadores históricos são arredondados a R$ 0,1 bilhão; percentuais recalculados são aproximados e podem diferir dos originais. O CSV conserva também o percentual originalmente exibido.

## Verificação

Conferidas todas as vinte renúncias nominais de 2023 por razão social contra o CSV bruto totalizador em centavos. Conferidos os dezoito EBITDAs originais da reconsulta contra a linha EBITDA e a coluna de encerramento nos snapshots `income_stmt.csv`; moeda e câmbio reproduzem o produto convertido. As reconsultas não substituem os valores históricos. Fórmula verificada para todas as razões calculáveis. Nenhum EBITDA ausente foi convertido em zero.

Navegador: seis abas, acesso direto pelo hash, vinte pares de barras, vinte linhas em cada tabela, seis moedas utilizadas, cores distintas e escala comum partindo de zero; downloads e navegação testados, sem erros JavaScript ou transbordamento no celular. Capturas arquivadas neste diretório. O gráfico não empilha renúncia e EBITDA.

## Suposições e riscos publicados na aba

- Base de preços: o numerador recebe o fator histórico 1,132563902179; o EBITDA permanece nominal. Isso eleva a razão em 13,26% frente à divisão nominal. Preservação explícita para reproduzir a escolha autorizada; não é uma comparação em poder de compra equivalente. O código histórico rotula julho/2026, mas só cadastra taxas até junho, com junho identificado como IPCA-15; não certificamos essa série contra o IBGE. As outras abas mantêm sua metodologia de IPCA definitivo.
- Escopo: valores globais não isolam as empresas brasileiras. FMC é aproximação setorial para Syngenta; Mitsui é aproximação para Modec e seu vínculo não foi validado. Nem as companhias diretamente mapeadas foram conciliadas contabilmente com os CNPJs. Confirmar perímetro e vínculo exige demonstrações e documentação societária.
- Moedas: taxas fixas do autor, sem certificação da atribuição ao BCB. Petrobras, Vale e Embraer mudam de BRL para USD por heurística de valor de mercado/receita. Confirmar moeda pode alterar materialmente o denominador.
- Período: MITSY encerra em março de 2023; a renúncia é do ano civil. Os demais disponíveis encerram em dezembro. Não houve fallback para outro ano nos snapshots disponíveis.
- Precisão: Petrobras histórica preservada em R$ 253,8 bi, contra reconsulta convertida de R$ 253,6162 bi. A causa da divergência é desconhecida sem snapshot da geração original. Percentuais são aproximados pelos denominadores arredondados.
- Ausência: Ventura sem ticker; Gol sem demonstração utilizável na consulta. Mantidas como n/d. A causa de uma consulta vazia não autoriza afirmar inexistência de EBITDA.
- Interpretação: EBITDA não é lucro líquido e a razão não demonstra causalidade, dependência nem participação da renúncia na formação do lucro. Não somar denominadores de escopos diferentes.
