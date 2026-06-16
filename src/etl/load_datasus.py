from __future__ import annotations

import argparse
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import pandas as pd
import pyreaddbc
from dbfread import DBF, FieldParser
from sqlalchemy import Integer, Text, create_engine, inspect, text


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATABASE_URL = "postgresql+psycopg://postgres:postgres@localhost:5432/sifilis_analytics"
PORTO_ALEGRE = "431490"


class ParserDatasInvalidas(FieldParser):
    def parseD(self, field, data):
        try:
            return super().parseD(field, data)
        except ValueError:
            return None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Carrega microdados DATASUS DBC no PostgreSQL analitico do anteprojeto."
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


def resolve_path(path: str | Path) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return ROOT / candidate


def read_dbc(path: Path) -> pd.DataFrame:
    with tempfile.TemporaryDirectory() as tmpdir:
        dbf_path = Path(tmpdir) / f"{path.stem}.dbf"
        pyreaddbc.dbc2dbf(str(path), str(dbf_path))
        table = DBF(
            str(dbf_path),
            encoding="iso-8859-1",
            parserclass=ParserDatasInvalidas,
            load=True,
        )
        return pd.DataFrame(iter(table))


def normalize_columns(columns: Iterable[str]) -> list[str]:
    normalized = []
    seen: dict[str, int] = {}
    for column in columns:
        name = str(column).strip().lower()
        if not name:
            name = "coluna_sem_nome"
        count = seen.get(name, 0)
        seen[name] = count + 1
        normalized.append(name if count == 0 else f"{name}_{count + 1}")
    return normalized


def normalize_value(value):
    if pd.isna(value):
        return None
    if hasattr(value, "isoformat"):
        return value.isoformat()
    value = str(value).strip()
    return value or None


def prepare_dataframe(df: pd.DataFrame, source_path: Path, source_system: str, year: int) -> pd.DataFrame:
    df = df.copy()
    df.columns = normalize_columns(df.columns)
    for column in df.columns:
        df[column] = df[column].map(normalize_value)
    df["source_year"] = year
    df["source_system"] = source_system
    df["source_file"] = source_path.name
    df["loaded_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    return df


def execute_sql_file(engine, path: Path) -> None:
    sql = path.read_text(encoding="utf-8")
    with engine.begin() as connection:
        connection.exec_driver_sql(sql)


def load_table(engine, df: pd.DataFrame, schema: str, table: str, year: int) -> None:
    inspector = inspect(engine)
    dtype = {column: Text() for column in df.columns}
    dtype["source_year"] = Integer()

    if not inspector.has_table(table, schema=schema):
        df.head(0).to_sql(table, engine, schema=schema, if_exists="append", index=False, dtype=dtype)

    with engine.begin() as connection:
        connection.execute(text(f"DELETE FROM {schema}.{table} WHERE source_year = :year"), {"year": year})

    df.to_sql(
        table,
        engine,
        schema=schema,
        if_exists="append",
        index=False,
        dtype=dtype,
        chunksize=2000,
        method="multi",
    )


def query_scalar(engine, sql: str):
    with engine.begin() as connection:
        return connection.execute(text(sql)).scalar_one()


def run_validation(engine, strict: bool) -> None:
    checks = {
        "SINAN/SIFCBR bruto": "SELECT COUNT(*) FROM bronze.sinan_sifilis_congenita",
        "SINASC bruto": "SELECT COUNT(*) FROM bronze.sinasc_nascidos_vivos",
        "SINAN Porto Alegre": (
            "SELECT COUNT(*) FROM silver.sinan_sifilis_congenita "
            "WHERE ano = 2024 AND cod_municipio_residencia = '431490'"
        ),
        "SINASC Porto Alegre": (
            "SELECT COUNT(*) FROM silver.sinasc_nascidos_vivos "
            "WHERE ano = 2024 AND cod_municipio_residencia = '431490'"
        ),
        "Maes negras sem pre-natal": (
            "SELECT COALESCE(SUM(casos_sc), 0) FROM gold.sinan_sc_sem_prenatal_escolaridade "
            "WHERE ano = 2024 AND cod_municipio_residencia = '431490' "
            "AND grupo_racial_mae = 'Maes negras'"
        ),
        "Maes nao negras sem pre-natal": (
            "SELECT COALESCE(SUM(casos_sc), 0) FROM gold.sinan_sc_sem_prenatal_escolaridade "
            "WHERE ano = 2024 AND cod_municipio_residencia = '431490' "
            "AND grupo_racial_mae = 'Maes nao negras'"
        ),
    }

    expected = {
        "SINAN/SIFCBR bruto": 12762,
        "SINASC bruto": 111988,
        "SINAN Porto Alegre": 137,
        "SINASC Porto Alegre": 12850,
        "Maes negras sem pre-natal": 10,
        "Maes nao negras sem pre-natal": 14,
    }

    print("\nValidacao da carga")
    for label, sql in checks.items():
        value = int(query_scalar(engine, sql))
        print(f"- {label}: {value}")
        if strict and value != expected[label]:
            raise AssertionError(f"{label}: esperado {expected[label]}, obtido {value}")


def main() -> None:
    args = parse_args()
    sinan_path = resolve_path(args.sinan)
    sinasc_path = resolve_path(args.sinasc)

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

    execute_sql_file(engine, ROOT / "database/init/002_views.sql")
    run_validation(engine, strict=args.strict)


if __name__ == "__main__":
    main()
