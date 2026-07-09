from __future__ import annotations

import argparse
import os
from dataclasses import asdict, dataclass
from pathlib import Path

import pandas as pd

from src.config import ROOT, load_project_env, resolve_project_path


CANDIDATE_YEAR_COLUMNS = ["ano", "ano_obito", "ano_nascimento", "ano_competencia", "ano_referencia"]
CANDIDATE_UF_COLUMNS = ["sigla_uf", "sigla_uf_residencia", "sigla_uf_estabelecimento"]
CANDIDATE_MUNICIPALITY_COLUMNS = [
    "id_municipio",
    "id_municipio_residencia",
    "id_municipio_estabelecimento",
    "id_municipio_nascimento",
]


@dataclass(frozen=True)
class BasedosdadosTable:
    table: str
    planned_use: str
    initial_decision: str

    @property
    def project(self) -> str:
        return self.table.split(".")[0]

    @property
    def dataset(self) -> str:
        return self.table.split(".")[1]

    @property
    def table_name(self) -> str:
        return self.table.split(".")[2]


@dataclass
class AuditRow:
    source: str
    table: str
    planned_use: str
    decision: str
    available_period: str
    year_column: str | None
    municipality_column: str | None
    estimated_bytes: str
    status: str


DEFAULT_TABLE_CONFIG = [
    (
        "BASEDOSDADOS_SINASC_TABLE",
        "basedosdados.br_ms_sinasc.microdados",
        "Nascidos vivos, denominador de incidencia e perfil materno",
        "validar",
    ),
    (
        "BASEDOSDADOS_SIM_TABLE",
        "basedosdados.br_ms_sim.microdados",
        "Mortalidade e desfechos agregados",
        "validar",
    ),
    (
        "BASEDOSDADOS_CNES_TABLE",
        "basedosdados.br_ms_cnes.estabelecimento",
        "Oferta assistencial por municipio/ano",
        "validar",
    ),
    (
        "BASEDOSDADOS_POPULACAO_TABLE",
        "basedosdados.br_ms_populacao.municipio",
        "Populacao municipal e contexto demografico",
        "validar",
    ),
    (
        "BASEDOSDADOS_SIH_SERVICOS_TABLE",
        "basedosdados.br_ms_sih.servicos_profissionais",
        "Contexto hospitalar/assistencial complementar",
        "opcional",
    ),
    (
        "BASEDOSDADOS_SINAN_REFERENCIA_TABLE",
        "basedosdados.br_ms_sinan.microdados_violencia",
        "Referencia tecnica para padrao de consumo SINAN, nao para sifilis congenita",
        "referencia",
    ),
]


def tables_from_env() -> list[BasedosdadosTable]:
    tables: list[BasedosdadosTable] = []
    for env_var, default_table, planned_use, initial_decision in DEFAULT_TABLE_CONFIG:
        table_id = os.getenv(env_var, default_table).strip()
        if table_id:
            tables.append(BasedosdadosTable(table_id, planned_use, initial_decision))
    return tables


def first_existing(columns: set[str], candidates: list[str]) -> str | None:
    for column in candidates:
        if column in columns:
            return column
    return None


def columns_sql(table: BasedosdadosTable) -> str:
    return f"""
SELECT column_name, data_type
FROM `{table.project}.{table.dataset}.INFORMATION_SCHEMA.COLUMNS`
WHERE table_name = '{table.table_name}'
ORDER BY ordinal_position
""".strip()


def period_sql(table: BasedosdadosTable, columns: set[str]) -> tuple[str, str | None, str | None]:
    year_column = first_existing(columns, CANDIDATE_YEAR_COLUMNS)
    uf_column = first_existing(columns, CANDIDATE_UF_COLUMNS)
    municipality_column = first_existing(columns, CANDIDATE_MUNICIPALITY_COLUMNS)

    if year_column is None:
        return f"SELECT COUNT(*) AS total_registros FROM `{table.table}`", None, municipality_column

    filters = []
    if uf_column:
        filters.append(f"{uf_column} = 'RS'")
    where_clause = f"WHERE {' AND '.join(filters)}" if filters else ""

    sql = f"""
SELECT
  MIN({year_column}) AS ano_minimo,
  MAX({year_column}) AS ano_maximo,
  COUNT(*) AS total_registros
FROM `{table.table}`
{where_clause}
""".strip()
    return sql, year_column, municipality_column


def year_series_sql(table: BasedosdadosTable, year_column: str, columns: set[str]) -> str:
    uf_column = first_existing(columns, CANDIDATE_UF_COLUMNS)
    filters = [f"{uf_column} = 'RS'"] if uf_column else []
    where_clause = f"WHERE {' AND '.join(filters)}" if filters else ""
    return f"""
SELECT
  {year_column} AS ano,
  COUNT(*) AS total_registros
FROM `{table.table}`
{where_clause}
GROUP BY ano
ORDER BY ano
""".strip()


def format_bytes(value: int | None) -> str:
    if value is None:
        return "nao estimado"
    gib = value / 1024**3
    return f"{gib:.3f} GiB"


def query_dataframe(client, sql: str) -> pd.DataFrame:
    rows = client.query(sql).result()
    return pd.DataFrame([dict(row.items()) for row in rows])


def dry_run_bytes(client, sql: str, max_bytes_billed: int) -> int | None:
    from google.cloud import bigquery

    job_config = bigquery.QueryJobConfig(
        dry_run=True,
        use_query_cache=False,
        maximum_bytes_billed=max_bytes_billed,
    )
    job = client.query(sql, job_config=job_config)
    return int(job.total_bytes_processed or 0)


def make_client(project_id: str | None):
    if not project_id:
        return None
    try:
        from google.cloud import bigquery
    except ImportError:
        return None
    return bigquery.Client(project=project_id)


def audit_tables(
    project_id: str | None,
    execute: bool,
    max_bytes_billed: int,
    tables: list[BasedosdadosTable] | None = None,
) -> pd.DataFrame:
    client = make_client(project_id)
    rows: list[AuditRow] = []

    for table in tables or tables_from_env():
        row = AuditRow(
            source="Base dos Dados",
            table=table.table,
            planned_use=table.planned_use,
            decision=table.initial_decision,
            available_period="a descobrir",
            year_column=None,
            municipality_column=None,
            estimated_bytes="nao estimado",
            status="pendente: configure GOOGLE_CLOUD_PROJECT e credenciais BigQuery",
        )

        if client is not None:
            try:
                columns = set(query_dataframe(client, columns_sql(table))["column_name"].astype(str))
                sql, year_column, municipality_column = period_sql(table, columns)
                row.year_column = year_column
                row.municipality_column = municipality_column
                row.estimated_bytes = format_bytes(dry_run_bytes(client, sql, max_bytes_billed))
                row.status = "dry_run ok"

                if execute:
                    result = query_dataframe(client, sql)
                    if not result.empty and {"ano_minimo", "ano_maximo"}.issubset(result.columns):
                        row.available_period = f"{result.loc[0, 'ano_minimo']}-{result.loc[0, 'ano_maximo']}"
                    else:
                        row.available_period = "sem coluna anual identificada"
                    row.status = "consulta executada"
            except Exception as exc:
                row.status = f"erro: {type(exc).__name__}: {exc}"

        rows.append(row)

    return pd.DataFrame([asdict(row) for row in rows])


def parse_args() -> argparse.Namespace:
    load_project_env()
    parser = argparse.ArgumentParser(description="Audita tabelas candidatas da Base dos Dados via BigQuery.")
    parser.add_argument(
        "--project-id",
        default=os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("GCP_PROJECT"),
        help="Projeto Google Cloud usado para billing e autenticacao.",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Executa consultas de periodo alem do dry_run. Sem esta flag, apenas estima bytes.",
    )
    parser.add_argument(
        "--max-bytes-billed",
        type=int,
        default=int(os.getenv("BIGQUERY_MAX_BYTES_BILLED", str(2 * 1024**3))),
        help="Limite de bytes faturados por query.",
    )
    parser.add_argument(
        "--output",
        default="data/profiles/basedosdados_audit.csv",
        help="Caminho do CSV de saida.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    audit = audit_tables(args.project_id, execute=args.execute, max_bytes_billed=args.max_bytes_billed)
    output = resolve_project_path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    audit.to_csv(output, index=False, encoding="utf-8")
    print(f"Auditoria salva em: {output.relative_to(ROOT)}")
    print(audit[["table", "decision", "estimated_bytes", "status"]].to_string(index=False))


if __name__ == "__main__":
    main()
