from __future__ import annotations

import argparse
import os

from sqlalchemy import create_engine

from src.config import DEFAULT_DATABASE_URL, ROOT
from src.etl.database import execute_sql_file, load_table
from src.etl.datasus_sources import parse_years, resolve_datasus_sources
from src.etl.dbc import read_dbc
from src.etl.transform import prepare_dataframe
from src.etl.validation import run_validation


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Carrega microdados DATASUS DBC no PostgreSQL analitico do projeto."
    )
    parser.add_argument("--year", type=int, default=2024, help="Ano de referencia dos arquivos carregados.")
    parser.add_argument(
        "--years",
        help="Anos a carregar. Aceita lista '2021,2022,2023' ou intervalo '2014:2024'.",
    )
    parser.add_argument(
        "--sinan",
        default="data/raw/SIFCBR24.dbc",
        help="Caminho para o arquivo DBC do SINAN/SIFCBR. Use apenas com carga de um ano.",
    )
    parser.add_argument(
        "--sinasc",
        default="data/raw/sinasc/DNRS2024.dbc",
        help="Caminho para o arquivo DBC do SINASC. Use apenas com carga de um ano.",
    )
    parser.add_argument(
        "--sinan-template",
        help="Template para SINAN/SIFCBR em cargas multi-ano. Aceita {year} e {yy}.",
    )
    parser.add_argument(
        "--sinasc-template",
        help="Template para SINASC em cargas multi-ano. Aceita {year} e {yy}.",
    )
    parser.add_argument(
        "--database-url",
        default=os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL),
        help="URL SQLAlchemy do PostgreSQL.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Valida contagens esperadas para os arquivos 2024 incluidos no repositorio.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    years = parse_years(args.year, args.years)
    multi_year = len(years) > 1 or args.years is not None
    if args.strict and years != [2024]:
        raise ValueError("--strict valida apenas o baseline 2024. Use --year 2024 --strict.")

    if multi_year and (args.sinan != "data/raw/SIFCBR24.dbc" or args.sinasc != "data/raw/sinasc/DNRS2024.dbc"):
        raise ValueError("Use --sinan-template e --sinasc-template para cargas multi-ano.")

    if multi_year:
        source_pairs, missing = resolve_datasus_sources(
            years,
            sinan_template=args.sinan_template,
            sinasc_template=args.sinasc_template,
        )
    else:
        source_pairs, missing = resolve_datasus_sources(years, sinan=args.sinan, sinasc=args.sinasc)

    if missing:
        detail = "\n".join(f"- {item}" for item in missing)
        raise FileNotFoundError(f"Arquivos DATASUS ausentes para a carga solicitada:\n{detail}")

    engine = create_engine(args.database_url)
    execute_sql_file(engine, ROOT / "database/init/001_schemas.sql")

    for source_pair in source_pairs:
        print(f"\nAno de referencia: {source_pair.year}")
        print(f"Lendo SINAN/SIFCBR: {source_pair.sinan}")
        sinan = prepare_dataframe(read_dbc(source_pair.sinan), source_pair.sinan, "SINAN/SIFCBR", source_pair.year)
        print(f"Carregando bronze.sinan_sifilis_congenita: {len(sinan)} linhas")
        load_table(engine, sinan, "bronze", "sinan_sifilis_congenita", source_pair.year)

        print(f"Lendo SINASC: {source_pair.sinasc}")
        sinasc = prepare_dataframe(read_dbc(source_pair.sinasc), source_pair.sinasc, "SINASC", source_pair.year)
        print(f"Carregando bronze.sinasc_nascidos_vivos: {len(sinasc)} linhas")
        load_table(engine, sinasc, "bronze", "sinasc_nascidos_vivos", source_pair.year)

    execute_sql_file(engine, ROOT / "database/init/010_silver_views.sql")
    execute_sql_file(engine, ROOT / "database/init/020_gold_views.sql")
    run_validation(engine, strict=args.strict)


if __name__ == "__main__":
    main()
