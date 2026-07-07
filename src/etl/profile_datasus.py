from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from src.config import ROOT, resolve_project_path
from src.etl.datasus_sources import DatasusSourcePair, parse_years, resolve_datasus_sources
from src.etl.dbc import read_dbc


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Gera perfis exploratorios dos arquivos DATASUS antes do schema analitico final."
    )
    parser.add_argument("--year", type=int, default=2024, help="Ano de referencia quando --years nao for usado.")
    parser.add_argument("--years", help="Anos a perfilar. Aceita lista '2021,2022' ou intervalo '2014:2024'.")
    parser.add_argument(
        "--output",
        default="data/profiles/datasus_column_profile.csv",
        help="Caminho do CSV de saida com perfil por coluna.",
    )
    return parser.parse_args()


def profile_dataframe(df: pd.DataFrame, source: str, year: int, path: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    total_rows = len(df)
    for column in df.columns:
        series = df[column]
        normalized = series.astype("string").str.strip()
        blank_or_null = normalized.isna() | normalized.eq("")
        rows.append(
            {
                "source": source,
                "year": year,
                "file": path.name,
                "column": column,
                "dtype": str(series.dtype),
                "rows": total_rows,
                "blank_or_null": int(blank_or_null.sum()),
                "blank_or_null_percent": round(float(blank_or_null.mean() * 100), 2) if total_rows else 0,
                "distinct_values": int(normalized[~blank_or_null].nunique()),
            }
        )
    return rows


def profile_pair(source_pair: DatasusSourcePair) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    sinan = read_dbc(source_pair.sinan)
    rows.extend(profile_dataframe(sinan, "SINAN/SIFCBR", source_pair.year, source_pair.sinan))

    sinasc = read_dbc(source_pair.sinasc)
    rows.extend(profile_dataframe(sinasc, "SINASC", source_pair.year, source_pair.sinasc))
    return rows


def main() -> None:
    args = parse_args()
    years = parse_years(args.year, args.years)
    source_pairs, missing = resolve_datasus_sources(years)
    if missing:
        detail = "\n".join(f"- {item}" for item in missing)
        raise FileNotFoundError(f"Arquivos DATASUS ausentes para profiling:\n{detail}")

    rows: list[dict[str, object]] = []
    for source_pair in source_pairs:
        print(f"Perfilando ano {source_pair.year}")
        rows.extend(profile_pair(source_pair))

    output = resolve_project_path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(output, index=False, encoding="utf-8")
    print(f"Perfil salvo em: {output.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
