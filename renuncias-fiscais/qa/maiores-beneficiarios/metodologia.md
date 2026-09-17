# Maiores Beneficiários — 17/09/2026

Recorte: todos os valores de 2015–2024, com 2024 parcial, em reais de agosto/2026. A regra de origem do IPCA é a já documentada: média janeiro–dezembro para 2015–2023 e janeiro–junho para 2024. Dados e rótulos são produzidos por scripts/11_export_apresentacao.py, no objeto beneficiarios de artifact/apresentacao.json.

## Concentração

Unidade: raiz (oito primeiros dígitos) de identificadores com formato de 14 dígitos. Não é consolidação por controlador ou por nome. Conta todas as raízes presentes, incluindo saldos nulos e negativos. São pessoas jurídicas, incluindo órgãos públicos; por isso o texto publicado fala em beneficiários, não apenas empresas. Nome exibido: razão social do estabelecimento de maior acumulado nominal, reproduzindo a escolha do ranking. Top 1%: arredondar para cima a quantidade de raízes; mostrar quantidade exata e percentual efetivo arredondado. Denominador monetário: saldo de toda a base, inclusive identificador inválido. Não remover negativos ou registros sem cadastro.

Resultados: 69.462 raízes; 695 maiores (1,000547%) concentram 82,891690%; top 10 = 25,568688%, top 100 = 55,586380%. Há 3 raízes com saldo real negativo (R$ -10.335,46). O identificador -3 soma R$ 200.294,89 em preços da referência, preservado no total mas não contado como empresa. Soma das raízes + identificador inválido fecha com o acumulado total, tolerância R$ 0,05 para somas DOUBLE.

## Setores

Aplica classificar_estabelecimentos, mesma classificação editorial em produção. Cada estabelecimento contribui para seu próprio setor. A soma dos setores fecha com cada total anual; o total de dez anos fecha com a Apresentação. “Não identificado” é mantido: aparece em nota com peso e na tabela completa. As barras destacam os dez maiores setores identificados; a evolução destaca os seis maiores do acumulado, não uma seleção diferente a cada ano. Gráfico de linhas em valores absolutos, sem empilhamento, para facilitar a comparação das trajetórias; 2024 é tracejado e marcado parcial.

Essa alocação difere do rótulo da raiz exibido no ranking: ali o setor acompanha o estabelecimento de maior acumulado nominal, e não representa necessariamente toda a atividade da raiz. Cadastro do snapshot aplicado a toda a série: não há histórico anual de CNAE/atividade. Não usar a evolução para afirmar mudança de atividade de uma empresa.

## Relação com o ranking e com Carabetta

Nosso ranking usa raiz do CNPJ, nominal de 2015–2023. A nova aba usa a mesma unidade, mas acumula 2015–2024 em preços de agosto/2026, podendo mudar posições. Não afirmar que as duas tabelas devem ser idênticas.

No código arquivado do Carabetta, gerar_relatorio_site.py:157–214 agrupa primeiro por razão social e CNPJ; depois aplica classificar_grupo_extenso ao nome para somar grupos. Sua tabela de razões sociais é agrupada pela string nome, não pela raiz. A concentração dele é por CNPJ completo. relatorio_abas.py:359–366 declara correspondência por padrões na razão social, primeiro padrão vence, sem QSA da Receita; “Outros” é residual. Portanto, grupo econômico é uma aproximação editorial por nome, não prova de controle societário. Não copiamos esse mapa nem o seu deflator.

## Verificação e limites

Exportador reconcilia os setores com os dez totais anuais e as raízes com o total. Navegador comparou setores calculados no banco com microdados embutidos (diferenças pequenas pelo arredondamento para reais inteiros do payload), testou acesso direto às novas abas, 20 linhas, dez barras, seis séries, filtros restritos ao Resumo e ausência de erros JavaScript. Capturas desktop e mobile arquivadas aqui.

Suposições: usa classificação cadastral atual em anos anteriores; não supõe que todas as raízes sejam empresas privadas nem que raiz equivalha a controlador. CNPJs com formato válido não tiveram a situação cadastral revalidada nesta edição. Negativos e identificador inválido seguem preservados como na auditoria original. Cobertura incompleta de 2024 impede ler a última variação como queda anual comparável. Fontes fiscais e IPCA permanecem as do snapshot documentado em ../apresentacao/metodologia.md.
