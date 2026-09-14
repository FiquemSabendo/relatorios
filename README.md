# Relatórios · Fiquem Sabendo

Relatórios e ferramentas de dados publicados pela [Fiquem Sabendo](https://fiquemsabendo.com.br).
Cada relatório vive em uma pasta própria, com pipeline reprodutível e README; o site
estático é servido pelo GitHub Pages a partir de `docs/`, no domínio `relatorios.fiquemsabendo.com.br`
(`docs/CNAME`).

**Site:** <https://relatorios.fiquemsabendo.com.br/>

| Relatório | Pasta | Página |
|---|---|---|
| Renúncias fiscais federais por CNPJ, 2015–2024 | [`renuncias-fiscais/`](renuncias-fiscais/) | [/renuncias-fiscais/](https://relatorios.fiquemsabendo.com.br/renuncias-fiscais/) |

## Estrutura

```
relatorios/
├── docs/                      # o que o GitHub Pages serve (branch main, pasta /docs)
│   ├── index.html             # índice dos relatórios
│   └── <relatorio>/index.html # página gerada de cada relatório
└── <relatorio>/               # fontes, scripts e README de cada relatório
```

## Como adicionar um relatório

1. Crie a pasta `<nome>/` com o pipeline e um `README.md` (fonte dos dados, como rodar, caveats).
2. Faça o build gravar a página em `docs/<nome>/index.html`.
3. Acrescente a linha na tabela acima e o card em `docs/index.html`.
4. Dados brutos e bancos locais ficam fora do git (`.gitignore` já cobre `*/data/raw/` e `*/*.duckdb`).
