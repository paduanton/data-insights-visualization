from __future__ import annotations

import argparse
import os

from src.config import DEFAULT_DATABASE_URL, ROOT, load_project_env
from src.etl.datasus_sources import parse_years, resolve_sim_sources


def parse_args() -> argparse.Namespace:
    load_project_env()
    parser = argparse.ArgumentParser(
        description="Carrega arquivos SIM/DO em bronze para analises complementares."
    )
    parser.add_argument("--year", type=int, default=2024, help="Ano de referencia quando --years nao for usado.")
    parser.add_argument("--years", help="Anos a carregar. Aceita lista '2021,2022' ou intervalo '2014:2024'.")
    parser.add_argument("--template", help="Template para SIM/DO. Aceita {year} e {yy}.")
    parser.add_argument(
        "--database-url",
        default=os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL),
        help="URL SQLAlchemy do PostgreSQL.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    years = parse_years(args.year, args.years)
    sources, missing = resolve_sim_sources(years, template=args.template)
    if missing:
        detail = "\n".join(f"- {item}" for item in missing)
        raise FileNotFoundError(f"Arquivos SIM ausentes para a carga solicitada:\n{detail}")

    from sqlalchemy import create_engine

    from src.etl.database import execute_sql_file, load_table
    from src.etl.dbc import read_dbc
    from src.etl.transform import prepare_dataframe

    engine = create_engine(args.database_url)
    execute_sql_file(engine, ROOT / "database/init/001_schemas.sql")

    for source in sources:
        print(f"\nAno de referencia: {source.year}")
        print(f"Lendo SIM/DO: {source.path}")
        sim = prepare_dataframe(read_dbc(source.path), source.path, source.source, source.year)
        print(f"Carregando bronze.sim_obitos: {len(sim)} linhas")
        load_table(engine, sim, "bronze", "sim_obitos", source.year)

    execute_sql_file(engine, ROOT / "database/init/031_sim_views.sql")


if __name__ == "__main__":
    main()
