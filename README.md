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
│   ├── CNAME                  # relatorios.fiquemsabendo.com.br
│   ├── index.html             # índice dos relatórios — GERADO por build_index.py
│   └── <relatorio>/index.html # página gerada de cada relatório
├── <relatorio>/               # fontes, scripts, README e relatorio.json de cada relatório
├── _identidade/               # logos e fontes da Fiquem Sabendo usados pelo índice
└── build_index.py             # monta docs/index.html a partir dos relatorio.json
```

## Como adicionar um relatório

1. Crie a pasta `<nome>/` com o pipeline e um `README.md` (fonte dos dados, como rodar, caveats).
2. Faça o build gravar a página em `docs/<nome>/index.html`.
3. Crie `<nome>/relatorio.json`:

   ```json
   {
     "titulo": "…",
     "descricao": "…",
     "tag": "Dados abertos",
     "fonte": "…",
     "acao": "Abrir o explorador",
     "publicado_em": "2026-09-11"
   }
   ```

4. Rode `python3 build_index.py` (ou só faça o push: o workflow `Índice dos relatórios`
   regenera `docs/index.html` e commita). Enquanto houver um único relatório, o índice
   redireciona para ele; a partir do segundo vira uma lista de cards, do mais recente para
   o mais antigo. `"oculto": true` tira um relatório do índice sem apagar nada.
5. Dados brutos e bancos locais ficam fora do git (`.gitignore` já cobre `*/data/raw/` e `*/*.duckdb`).
