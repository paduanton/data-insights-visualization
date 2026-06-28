from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import pandas as pd


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


def classify_racial_group(value: object) -> str:
    code = str(value).strip()
    if code in {"2", "4"}:
        return "Maes negras"
    if code in {"1", "3", "5"}:
        return "Maes nao negras"
    return "Ignorado/sem informacao"


def classify_sinan_schooling(value: object) -> str:
    code = str(value).strip()
    if code in {"02", "03", "04", "05"}:
        return "Ate 7 anos de estudo"
    if code in {"06", "07", "08"}:
        return "8 anos ou mais de estudo"
    return "Ignorada/sem informacao"


def classify_sinan_prenatal(value: object) -> str:
    code = str(value).strip()
    if code == "1":
        return "Com pre-natal"
    if code == "2":
        return "Sem pre-natal"
    return "Ignorado/sem informacao"
