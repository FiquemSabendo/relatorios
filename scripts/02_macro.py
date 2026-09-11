#!/usr/bin/env python3
"""Baixa as séries macro usadas para deflacionar e normalizar as renúncias.

IPCA  : SIDRA tabela 1737, variável 2266 — número-índice mensal (dez/1993 = 100).
        Consolidado pela MÉDIA ANUAL do índice, que é o deflator correto para um
        fluxo distribuído ao longo do ano (usar dezembro superestima a correção).
PIB   : SIDRA tabela 1846, variável 585, categoria 90707 — PIB a preços de mercado,
        valores correntes, trimestral, em R$ milhões. Consolidado pela soma dos
        4 trimestres do ano.

Saída: data/macro/ipca.csv e data/macro/pib.csv
"""
import csv
import json
import os
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "macro")

IPCA_URL = "https://apisidra.ibge.gov.br/values/t/1737/n1/all/v/2266/p/all"
PIB_URL = "https://apisidra.ibge.gov.br/values/t/1846/n1/all/v/585/p/all/c11255/90707"


def sidra(url):
    req = urllib.request.Request(url, headers={"User-Agent": "renuncias-etl/1.0"})
    with urllib.request.urlopen(req, timeout=180) as r:
        data = json.load(r)
    if len(data) < 2:
        raise SystemExit(f"SIDRA devolveu resposta vazia: {url}")
    return data[1:]  # a primeira linha é o cabeçalho descritivo


def main():
    os.makedirs(OUT, exist_ok=True)

    # ---- IPCA: média anual do número-índice -------------------------------
    meses = {}
    for row in sidra(IPCA_URL):
        periodo = row["D3C"]          # AAAAMM
        valor = row["V"]
        if valor in ("...", "-", "..", None):
            continue
        meses.setdefault(periodo[:4], []).append(float(valor))

    ipca = []
    for ano in sorted(meses):
        v = meses[ano]
        # só anos completos entram na média (o ano corrente parcial é descartado)
        if len(v) == 12:
            ipca.append((int(ano), sum(v) / 12, len(v)))

    with open(os.path.join(OUT, "ipca.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["ano", "ipca_indice_medio", "meses"])
        w.writerows([(a, f"{i:.6f}", n) for a, i, n in ipca])

    # ---- PIB nominal: soma dos 4 trimestres --------------------------------
    tris = {}
    for row in sidra(PIB_URL):
        periodo = row["D3C"]          # AAAAT
        valor = row["V"]
        if valor in ("...", "-", "..", None):
            continue
        tris.setdefault(periodo[:4], []).append(float(valor))

    pib = [(int(a), sum(v) * 1e6, len(v)) for a, v in sorted(tris.items()) if len(v) == 4]

    with open(os.path.join(OUT, "pib.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["ano", "pib_nominal_reais", "trimestres"])
        w.writerows([(a, f"{p:.0f}", n) for a, p, n in pib])

    ianos = {a for a, _, _ in ipca}
    panos = {a for a, _, _ in pib}
    faltando = [a for a in range(2015, 2025) if a not in ianos or a not in panos]
    if faltando:
        print(f"AVISO: sem série macro completa para {faltando}", file=sys.stderr)

    print(f"IPCA: {len(ipca)} anos ({min(ianos)}–{max(ianos)})")
    print(f"PIB : {len(pib)} anos ({min(panos)}–{max(panos)})")
    for a, p, _ in pib:
        if a >= 2015:
            idx = next(i for y, i, _ in ipca if y == a)
            print(f"  {a}  PIB R$ {p/1e12:6.2f} tri   IPCA idx {idx:8.2f}")


if __name__ == "__main__":
    main()
