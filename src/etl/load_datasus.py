from __future__ import annotations

import argparse
import os

from sqlalchemy import create_engine

from src.config import DEFAULT_DATABASE_URL, ROOT, resolve_project_path
from src.etl.database import execute_sql_file, load_table
from src.etl.dbc import read_dbc
from src.etl.transform import prepare_dataframe
from src.etl.validation import run_validation


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Carrega microdados DATASUS DBC no PostgreSQL analitico do projeto."
    )
    parser.add_argument("--year", type=int, default=2024, help="Ano de referencia dos arquivos carregados.")
    parser.add_argument(
        "--sinan",
        default="data/raw/SIFCBR24.dbc",
        help="Caminho para o arquivo DBC do SINAN/SIFCBR.",
    )
    parser.add_argument(
        "--sinasc",
        default="data/raw/sinasc/DNRS2024.dbc",
        help="Caminho para o arquivo DBC do SINASC.",
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
    sinan_path = resolve_project_path(args.sinan)
    sinasc_path = resolve_project_path(args.sinasc)

    if not sinan_path.exists():
        raise FileNotFoundError(f"Arquivo SINAN nao encontrado: {sinan_path}")
    if not sinasc_path.exists():
        raise FileNotFoundError(f"Arquivo SINASC nao encontrado: {sinasc_path}")

    engine = create_engine(args.database_url)
    execute_sql_file(engine, ROOT / "database/init/001_schemas.sql")

    print(f"Lendo SINAN/SIFCBR: {sinan_path}")
    sinan = prepare_dataframe(read_dbc(sinan_path), sinan_path, "SINAN/SIFCBR", args.year)
    print(f"Carregando bronze.sinan_sifilis_congenita: {len(sinan)} linhas")
    load_table(engine, sinan, "bronze", "sinan_sifilis_congenita", args.year)

    print(f"Lendo SINASC: {sinasc_path}")
    sinasc = prepare_dataframe(read_dbc(sinasc_path), sinasc_path, "SINASC", args.year)
    print(f"Carregando bronze.sinasc_nascidos_vivos: {len(sinasc)} linhas")
    load_table(engine, sinasc, "bronze", "sinasc_nascidos_vivos", args.year)

    execute_sql_file(engine, ROOT / "database/init/010_silver_views.sql")
    execute_sql_file(engine, ROOT / "database/init/020_gold_views.sql")
    run_validation(engine, strict=args.strict)


if __name__ == "__main__":
    main()
