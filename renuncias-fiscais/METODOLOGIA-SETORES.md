# Setor detalhado no ranking de empresas

Versão: 2026-09-17.1. Classificação editorial da Fiquem Sabendo, não uma classificação oficial do IBGE nem uma identificação de grupo econômico.

## O que a coluna descreve

A seção da CNAE original agrupa atividades muito diferentes: “Indústrias de transformação” inclui medicamentos, aviões, tabaco e automóveis. A coluna **Setor detalhado** oferece rótulos legíveis com base na atividade informada, como Aérea, Tabaco, Construção Civil, Farmacêutico, Fertilizantes, Automóveis e Indústria aeronáutica. A seção e a descrição da CNAE original são preservadas.

A classificação começa em cada CNPJ de estabelecimento. No ranking por raiz, a coluna acompanha o mesmo estabelecimento representativo já usado para nome e CNAE: aquele com maior renúncia nominal acumulada em todos os anos do snapshot (2015–2024, incluindo 2024 parcial). Não representa todas as atividades da raiz, não muda com os filtros e não junta empresas de raízes diferentes. Se a raiz for diversificada, seu rótulo pode esconder atividades secundárias; a auditoria exporta a quantidade de setores distintos por raiz.

## Fontes e regras, em ordem

1. **CNAE declarada na base de renúncias.** Usa-se a classe de cinco dígitos armazenada em `dim_estab`, com o cadastro mais recente disponível no pipeline. A classificação prioriza correspondência exata de classe, depois grupo (três dígitos), depois divisão (dois dígitos). A versão do catálogo oficial consultada em 17/09/2026 está preservada em `qa/setores-detalhados/cnae-ibge.json`. Todas as classes não nulas presentes na base foram encontradas nesse catálogo.
2. **Curadoria documentada, apenas quando o código está ausente/não mapeado.** O arquivo `data/classificacao-setorial/curadoria.json` associa uma raiz identificada a um setor e registra URL, evidência e data. Nesta versão inclui GE Celma, Construtora Ápia e Álya Construtora. A atividade não é deduzida apenas de palavras como “construtora” ou da marca de uma controladora. A GE é documentada por fonte corporativa; Ápia e Álya têm documentos com identificação do CNPJ. Nenhuma exceção é estendida a outras raízes do grupo.
3. **Inferência limitada à mesma raiz.** Se o estabelecimento não possui classificação e todos os rótulos obtidos das CNAEs conhecidas de outros estabelecimentos da mesma raiz concordam, pode receber esse rótulo. O resultado é explicitamente marcado “Inferido de outros CNPJs da mesma raiz”. Não se preenche nem altera o código CNAE original. Não há inferência transitiva a partir de outros rótulos inferidos.
4. **Não identificado.** Sem código utilizável, sem fonte específica e sem concordância entre atividades conhecidas da raiz, a classificação permanece ausente. Essas linhas e seus valores não são descartados.

As regras completas estão nos dicionários `ESPECIFICAS` e `DIVISOES` de `scripts/classificacao_setorial.py`. O resultado por classe, com descrição original e descrição IBGE, está em `qa/setores-detalhados/dicionario_cnae_setor.csv`. O resultado por CNPJ contém `setor_detalhado`, `regra`, `fonte` e `evidencia` em `classificacao_por_cnpj.csv`.

## Fronteiras editoriais

- **Aérea:** transporte aéreo; fabricação de aviões é “Indústria aeronáutica”, e manutenção identificável é “Manutenção aeronáutica”. Serviços aeroportuários não são tratados como companhia aérea.
- **Tabaco:** fabricação de produtos do fumo e comércio atacadista específico. Uma classe varejista que mistura alimentos e fumo recebe “Comércio de alimentos e tabaco”; não se presume tabaco exclusivo. Cultivo agrícola não é automaticamente indústria de tabaco.
- **Construção Civil:** construção de edifícios, infraestrutura e serviços especializados, além de casos documentados. Fabricantes de máquinas e vendedores de materiais de construção ficam em categorias próprias. Nem toda empresa que usa “construtora” no nome atua em construção civil.
- Algumas cadeias, como farmacêutica ou tabaco, reúnem fabricação e comércio específico; outras mantêm rótulos separados. Os rótulos são instrumentos de leitura, não uma classificação de insumo-produto ou uma medida de participação no mercado.
- Rótulos genéricos existentes na CNAE, como comércio não especializado e holdings, permanecem genéricos. Não se atribui uma atividade operacional específica sem evidência.

## Exibição

A coluna nova aparece ao lado de **Setor (seção CNAE)**. A busca textual também encontra o setor detalhado. Ao abrir a linha, o leitor vê o método e a evidência utilizados para o estabelecimento representativo. Os filtros e os gráficos setoriais anteriores continuam baseados na seção CNAE; não foram recalculados com esta classificação.

## Limitações e suposições

A CNAE é declarada pela fonte e pode estar desatualizada ou não representar a atividade mais relevante economicamente. A inferência entre estabelecimentos assume homogeneidade quando os dados conhecidos concordam; uma filial sem código pode, ainda assim, ter atividade diferente. Curadoria identifica a atividade documentada, mas não garante que ela tenha sido a mesma em todos os anos. Esta é uma classificação estática do cadastro do snapshot, não uma série anual de mudanças de setor.

A responsabilidade pelos dados originais é da fonte primária. Ausência de identificação não significa ausência de atividade. Estar no ranking não indica irregularidade. Revisões de CNAE ou novas fontes podem mudar rótulos, mas não devem alterar os valores fiscais. Mudanças nas regras devem incrementar a versão e produzir uma comparação das classificações.

## Reprodução e conferências

Da raiz do repositório:

```bash
python3 renuncias-fiscais/scripts/11_auditar_setores.py
python3 renuncias-fiscais/scripts/04_export_payload.py --somente-setores
python3 renuncias-fiscais/scripts/05_build_artifact.py
```

O modo `--somente-setores` verifica alinhamento de CNPJ e CNAE com o payload existente e atualiza apenas a classificação. Ele preserva integralmente os valores publicados, inclusive seus arredondamentos. A exportação completa também inclui a nova coluna, quando houver atualização integral da base.

A auditoria mede cobertura por método, por setor e por valor, verifica uma saída para cada CNPJ e a igualdade da soma antes/depois. A interface foi conferida em navegador, com buscas, abertura de detalhes e viewport móvel. Arquivos e resultados em `qa/setores-detalhados/`.

Fontes: [CNAE/IBGE](https://servicodados.ibge.gov.br/api/v2/cnae/classes), [Portal da Transparência](https://portaldatransparencia.gov.br/dicionario-de-dados/renuncias), [GE Celma](https://www.geaerospace.com/pt-br/facilities-latam-celma), [Construtora Ápia](https://www.grupoapia.com.br/) e publicação legal da Álya identificada no arquivo de curadoria.
