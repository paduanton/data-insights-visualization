from __future__ import annotations

import tempfile
from pathlib import Path

import pandas as pd
import pyreaddbc
from dbfread import DBF, FieldParser


class ParserDatasInvalidas(FieldParser):
    def parseD(self, field, data):
        try:
            return super().parseD(field, data)
        except ValueError:
            return None


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
