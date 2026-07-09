from __future__ import annotations

import argparse
import os

import pandas as pd

from src.config import DEFAULT_DATABASE_URL, ROOT, load_project_env
from src.etl.datasus_sources import parse_years


def parse_args() -> argparse.Namespace:
    load_project_env()
    parser = argparse.ArgumentParser(
        description="Carrega fontes auxiliares da Base dos Dados no PostgreSQL analitico."
    )
    parser.add_argument("--year", type=int, default=2024, help="Ano de referencia quando --years nao for usado.")
    parser.add_argument("--years", help="Anos a carregar. Aceita lista '2021,2022' ou intervalo '2015:2024'.")
    parser.add_argument(
        "--uf-prefix",
        default="43",
        help="Prefixo IBGE da UF para filtrar municipios. Rio Grande do Sul = 43.",
    )
    parser.add_argument(
        "--population-table",
        default=os.getenv("BASEDOSDADOS_POPULACAO_TABLE", "basedosdados.br_ms_populacao.municipio"),
        help="Tabela BigQuery de populacao municipal.",
    )
    parser.add_argument(
        "--project-id",
        default=os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("GCP_PROJECT"),
        help="Projeto Google Cloud usado para billing e autenticacao.",
    )
    parser.add_argument(
        "--database-url",
        default=os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL),
        help="URL SQLAlchemy do PostgreSQL.",
    )
    parser.add_argument(
        "--max-bytes-billed",
        type=int,
        default=int(os.getenv("BIGQUERY_MAX_BYTES_BILLED", str(2 * 1024**3))),
        help="Limite de bytes faturados por query.",
    )
    parser.add_argument(
        "--query-timeout-seconds",
        type=int,
        default=int(os.getenv("BIGQUERY_QUERY_TIMEOUT_SECONDS", "60")),
        help="Timeout por chamada ao BigQuery.",
    )
    return parser.parse_args()


def log(message: str = "") -> None:
    print(message, flush=True)


def population_sql(table: str) -> str:
    return f"""
SELECT
  ano,
  SUBSTR(id_municipio, 1, 6) AS cod_municipio,
  id_municipio,
  SUM(populacao) AS populacao_residente
FROM `{table}`
WHERE ano BETWEEN @start_year AND @end_year
  AND STARTS_WITH(id_municipio, @uf_prefix)
GROUP BY ano, cod_municipio, id_municipio
ORDER BY ano, cod_municipio
""".strip()


def normalize_population_dataframe(data: pd.DataFrame, table: str, years: list[int]) -> pd.DataFrame:
    if data.empty:
        return data

    normalized = data[data["ano"].isin(years)].copy()
    if normalized.empty:
        return normalized

    normalized["source"] = "Base dos Dados"
    normalized["source_table"] = table
    normalized["source_year"] = normalized["ano"].astype(int)
    for column in ["ano", "cod_municipio", "id_municipio", "populacao_residente", "source", "source_table"]:
        normalized[column] = normalized[column].astype(str)
    return normalized[
        [
            "source_year",
            "ano",
            "cod_municipio",
            "id_municipio",
            "populacao_residente",
            "source",
            "source_table",
        ]
    ]


def read_population_from_bigquery(
    project_id: str,
    table: str,
    years: list[int],
    uf_prefix: str,
    max_bytes_billed: int,
    query_timeout_seconds: int,
) -> pd.DataFrame:
    from google.cloud import bigquery

    client = bigquery.Client(project=project_id)
    job_config = bigquery.QueryJobConfig(
        maximum_bytes_billed=max_bytes_billed,
        query_parameters=[
            bigquery.ScalarQueryParameter("start_year", "INT64", min(years)),
            bigquery.ScalarQueryParameter("end_year", "INT64", max(years)),
            bigquery.ScalarQueryParameter("uf_prefix", "STRING", uf_prefix),
        ],
    )
    rows = client.query(population_sql(table), job_config=job_config, timeout=query_timeout_seconds).result(
        timeout=query_timeout_seconds
    )
    data = pd.DataFrame([dict(row.items()) for row in rows])
    return normalize_population_dataframe(data, table, years)


def main() -> None:
    args = parse_args()
    if not args.project_id:
        raise ValueError("Configure GOOGLE_CLOUD_PROJECT no .env ou informe --project-id.")

    years = parse_years(args.year, args.years)
    log(f"Carregando populacao municipal Base dos Dados: {min(years)}-{max(years)}")
    population = read_population_from_bigquery(
        project_id=args.project_id,
        table=args.population_table,
        years=years,
        uf_prefix=args.uf_prefix,
        max_bytes_billed=args.max_bytes_billed,
        query_timeout_seconds=args.query_timeout_seconds,
    )
    if population.empty:
        raise ValueError("A consulta de populacao municipal nao retornou registros.")

    from sqlalchemy import create_engine

    from src.etl.database import execute_sql_file, load_table

    engine = create_engine(args.database_url)
    execute_sql_file(engine, ROOT / "database/init/001_schemas.sql")

    for year in years:
        frame = population[population["source_year"] == year].copy()
        log(f"Carregando bronze.basedosdados_populacao_municipio {year}: {len(frame)} linhas")
        load_table(engine, frame, "bronze", "basedosdados_populacao_municipio", year)

    execute_sql_file(engine, ROOT / "database/init/032_basedosdados_views.sql")


if __name__ == "__main__":
    main()
