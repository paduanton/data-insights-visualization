from __future__ import annotations

from pathlib import Path

import pandas as pd
from sqlalchemy import Integer, Text, inspect, text


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
