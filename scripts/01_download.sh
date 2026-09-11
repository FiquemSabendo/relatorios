#!/usr/bin/env bash
# Baixa e extrai os microdados de Renúncias Fiscais do Portal da Transparência.
# Fonte: https://portaldatransparencia.gov.br/download-de-dados/renuncias
# O link do portal redireciona (302) para o bucket abaixo.
set -euo pipefail

BASE="https://dadosabertos-download.cgu.gov.br/PortalDaTransparencia/saida/renuncias"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
RAW="$ROOT/data/raw"
ANOS=${ANOS:-"2015 2016 2017 2018 2019 2020 2021 2022 2023 2024"}

mkdir -p "$RAW/zips"
: > "$RAW/manifest.tsv"
printf 'ano\tbytes\tlast_modified\tbaixado_em\n' >> "$RAW/manifest.tsv"

for ano in $ANOS; do
  zip="$RAW/zips/${ano}_RenunciasFiscais.zip"
  url="$BASE/${ano}_RenunciasFiscais.zip"

  if [[ ! -s "$zip" ]]; then
    echo ">> baixando $ano"
    curl -fsS --retry 3 --max-time 900 -o "$zip" "$url"
  else
    echo ">> $ano já baixado, pulando"
  fi

  lm=$(curl -fsSI --max-time 60 "$url" | grep -i '^last-modified:' | sed 's/^[Ll]ast-[Mm]odified: //' | tr -d '\r')
  printf '%s\t%s\t%s\t%s\n' "$ano" "$(stat -c%s "$zip")" "$lm" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$RAW/manifest.tsv"

  mkdir -p "$RAW/$ano"
  unzip -o -q "$zip" -d "$RAW/$ano"
done

echo
echo "Manifesto:"
column -t -s$'\t' "$RAW/manifest.tsv"
