# Composição das renúncias e custo fiscal

Implementação e conferência: 18/09/2026. Reprodução: executar `scripts/15_export_composicao_custo.py` e depois `scripts/05_build_artifact.py` a partir da raiz do projeto. O primeiro script utiliza a base DuckDB já validada e os fatores de `artifact/apresentacao.json`.

## Composição

Os 301 itens de `dim_item` são associados aos valores de `fato_item_ano`. Tipo, benefício, tributo e fundamento legal preservam os campos da fonte. O mecanismo segue a classificação existente em `scripts/03_build_db.sql`; o tema editorial é um agrupamento exclusivo dos mecanismos, documentado integralmente em `temas.json` e no script exportador. Não é um campo oficial, setor CNAE ou evidência de efetividade da política. Não houve revisão jurídica individual da vigência das normas.

Regimes genéricos não permitem identificar uma finalidade específica: mantidos em “Tema não determinado”. Farmacêuticos e químicos ficam em indústria, sem imputar toda a categoria à saúde. As classificações são hipóteses editoriais revisáveis; o fundamento original acompanha os resultados para permitir contestação.

Valores negativos e repetições são preservados conforme a base publicada. A composição usa preços de agosto/2026, com os fatores já adotados no projeto: média anual do IPCA na origem para anos completos e média de janeiro a junho para 2024. O acervo é parcial e não representa todos os gastos tributários federais.

## Custo fiscal

Fonte única das despesas: [Resultado do Tesouro Nacional, dezembro de 2023](https://www.tesourotransparente.gov.br/publicacoes/boletim-resultado-do-tesouro-nacional-rtn/2023/12), publicado em 29/01/2024. Planilha e boletim originais estão em `fontes/`; URLs e hashes estão no JSON de dados e na validação. Aba 2.2, coluna AB (2023), unidade R$ milhões correntes, convertida para reais. As células e os escopos de cada rubrica estão na aba pública e em `validacao.json`.

Usamos pagamentos efetivos, conforme nota 2 do boletim (p. 19), conferida visualmente e por extração de texto. Não são dotações ou empenhos. As despesas podem incluir obrigações de exercícios anteriores. A tentativa de consultar o glossário do Portal encontrou bloqueio de acesso; a definição utilizada é a nota oficial do próprio RTN.

A comparação é 2023 contra 2023, nominal, sem IPCA. Difere do exemplo arquivado de Carabetta que compara renúncias de 2023 com Bolsa Família de 2024. Bolsa inclui Auxílio Brasil; BPC inclui RMV; Fundeb é apenas complementação federal; RGPS não abrange toda a previdência pública; Minha Casa Minha Vida é a rubrica do RTN e não todo financiamento habitacional. Preservamos a edição histórica, sujeita a diferenças em revisões posteriores. Não se deve interpretar a razão como receita recuperável ou financiamento automático de outro programa.

## Validação

- 20 reconciliações: composição nominal e real fecha com os totais de cada ano de 2015–2024, diferença inferior a R$ 0,01.
- Cada um dos seis comparadores anuais confere com a soma independente dos 12 meses da aba 1.2, diferença inferior a R$ 0,01.
- Despesa primária total fecha com as quatro rubricas exaustivas 4.1 a 4.4; não são somados subitens sobrepostos.
- Navegação pelas sete abas, ausência da aba antiga, filtros encadeados e busca sem resultado verificados no Chromium. Sem erro JavaScript e sem transbordamento horizontal da página em 1300 e 420 pixels. Tabelas têm rolagem própria.
- Capturas das duas abas nas duas larguras acompanham esta documentação. O roteiro de navegação está em `test_interface.py`.
