from __future__ import annotations

import argparse
from pathlib import Path

from src.config import ROOT, resolve_project_path
from src.etl.datasus_sources import (
    DatasusSingleSource,
    DatasusSourcePair,
    parse_years,
    resolve_cnes_sources,
    resolve_datasus_sources,
    resolve_sim_sources,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Gera perfis exploratorios dos arquivos DATASUS antes do schema analitico final."
    )
    parser.add_argument("--year", type=int, default=2024, help="Ano de referencia quando --years nao for usado.")
    parser.add_argument("--years", help="Anos a perfilar. Aceita lista '2021,2022' ou intervalo '2014:2024'.")
    parser.add_argument("--skip-core", action="store_true", help="Nao perfila SINAN/SIFCBR e SINASC.")
    parser.add_argument("--include-cnes", action="store_true", help="Inclui CNES/ST no profiling.")
    parser.add_argument("--include-sim", action="store_true", help="Inclui SIM/DO no profiling.")
    parser.add_argument("--cnes-month", type=int, default=12, help="Mes CNES usado como snapshot anual.")
    parser.add_argument(
        "--output",
        default="data/profiles/datasus_column_profile.csv",
        help="Caminho do CSV de saida com perfil por coluna.",
    )
    return parser.parse_args()


def profile_dataframe(df, source: str, year: int, path: Path) -> list[dict[str, object]]:
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
    from src.etl.dbc import read_dbc

    rows: list[dict[str, object]] = []
    sinan = read_dbc(source_pair.sinan)
    rows.extend(profile_dataframe(sinan, "SINAN/SIFCBR", source_pair.year, source_pair.sinan))

    sinasc = read_dbc(source_pair.sinasc)
    rows.extend(profile_dataframe(sinasc, "SINASC", source_pair.year, source_pair.sinasc))
    return rows


def profile_single_source(source: DatasusSingleSource) -> list[dict[str, object]]:
    from src.etl.dbc import read_dbc

    df = read_dbc(source.path)
    return profile_dataframe(df, source.source, source.year, source.path)


def main() -> None:
    args = parse_args()
    years = parse_years(args.year, args.years)
    source_pairs = []
    missing: list[str] = []
    if not args.skip_core:
        source_pairs, missing = resolve_datasus_sources(years)
    extra_sources: list[DatasusSingleSource] = []
    if args.include_cnes:
        cnes_sources, cnes_missing = resolve_cnes_sources(years, month=args.cnes_month)
        extra_sources.extend(cnes_sources)
        missing.extend(cnes_missing)
    if args.include_sim:
        sim_sources, sim_missing = resolve_sim_sources(years)
        extra_sources.extend(sim_sources)
        missing.extend(sim_missing)

    if missing:
        detail = "\n".join(f"- {item}" for item in missing)
        raise FileNotFoundError(f"Arquivos DATASUS ausentes para profiling:\n{detail}")

    rows: list[dict[str, object]] = []
    for source_pair in source_pairs:
        print(f"Perfilando ano {source_pair.year}")
        rows.extend(profile_pair(source_pair))
    for source in extra_sources:
        print(f"Perfilando {source.source} {source.year}")
        rows.extend(profile_single_source(source))

    output = resolve_project_path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    import pandas as pd

    pd.DataFrame(rows).to_csv(output, index=False, encoding="utf-8")
    print(f"Perfil salvo em: {output.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
