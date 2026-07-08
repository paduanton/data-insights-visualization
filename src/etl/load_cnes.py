from __future__ import annotations

import argparse
import os

from src.config import DEFAULT_DATABASE_URL, ROOT
from src.etl.datasus_sources import parse_years, resolve_cnes_sources


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Carrega arquivos CNES/ST em bronze para analises complementares."
    )
    parser.add_argument("--year", type=int, default=2024, help="Ano de referencia quando --years nao for usado.")
    parser.add_argument("--years", help="Anos a carregar. Aceita lista '2021,2022' ou intervalo '2014:2024'.")
    parser.add_argument("--month", type=int, default=12, help="Mes CNES usado como snapshot anual.")
    parser.add_argument("--template", help="Template para CNES/ST. Aceita {year} e {yy}.")
    parser.add_argument(
        "--database-url",
        default=os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL),
        help="URL SQLAlchemy do PostgreSQL.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    years = parse_years(args.year, args.years)
    sources, missing = resolve_cnes_sources(years, month=args.month, template=args.template)
    if missing:
        detail = "\n".join(f"- {item}" for item in missing)
        raise FileNotFoundError(f"Arquivos CNES ausentes para a carga solicitada:\n{detail}")

    from sqlalchemy import create_engine

    from src.etl.database import execute_sql_file, load_table
    from src.etl.dbc import read_dbc
    from src.etl.transform import prepare_dataframe

    engine = create_engine(args.database_url)
    execute_sql_file(engine, ROOT / "database/init/001_schemas.sql")

    for source in sources:
        print(f"\nAno de referencia: {source.year}")
        print(f"Lendo CNES/ST: {source.path}")
        cnes = prepare_dataframe(read_dbc(source.path), source.path, source.source, source.year)
        cnes = cnes.assign(source_month=f"{args.month:02d}")
        print(f"Carregando bronze.cnes_estabelecimentos: {len(cnes)} linhas")
        load_table(engine, cnes, "bronze", "cnes_estabelecimentos", source.year)

    execute_sql_file(engine, ROOT / "database/init/030_cnes_views.sql")


if __name__ == "__main__":
    main()
