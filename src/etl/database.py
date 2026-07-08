from __future__ import annotations

from pathlib import Path

import pandas as pd
from sqlalchemy import Integer, Text, inspect, text


def quote_identifier(identifier: str) -> str:
    return f'"{identifier.replace(chr(34), chr(34) * 2)}"'


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
    else:
        existing_columns = {column["name"] for column in inspector.get_columns(table, schema=schema)}
        missing_columns = [column for column in df.columns if column not in existing_columns]
        if missing_columns:
            qualified_table = f"{quote_identifier(schema)}.{quote_identifier(table)}"
            with engine.begin() as connection:
                for column in missing_columns:
                    connection.execute(text(f"ALTER TABLE {qualified_table} ADD COLUMN {quote_identifier(column)} TEXT"))

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
