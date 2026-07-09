import pandas as pd

from src.etl.load_basedosdados import normalize_population_dataframe, population_sql


def test_population_sql_filters_year_period_and_uf_prefix():
    sql = population_sql("basedosdados.br_ms_populacao.municipio")

    assert "FROM `basedosdados.br_ms_populacao.municipio`" in sql
    assert "ano BETWEEN @start_year AND @end_year" in sql
    assert "STARTS_WITH(id_municipio, @uf_prefix)" in sql
    assert "SUM(populacao) AS populacao_residente" in sql


def test_normalize_population_dataframe_filters_years_and_adds_source_columns():
    data = pd.DataFrame(
        [
            {"ano": 2023, "cod_municipio": "431490", "id_municipio": "4314902", "populacao_residente": 100},
            {"ano": 2024, "cod_municipio": "431490", "id_municipio": "4314902", "populacao_residente": 120},
            {"ano": 2025, "cod_municipio": "431490", "id_municipio": "4314902", "populacao_residente": 130},
        ]
    )

    normalized = normalize_population_dataframe(
        data,
        table="basedosdados.br_ms_populacao.municipio",
        years=[2023, 2024],
    )

    assert normalized["source_year"].tolist() == [2023, 2024]
    assert normalized["ano"].tolist() == ["2023", "2024"]
    assert normalized["populacao_residente"].tolist() == ["100", "120"]
    assert normalized["source"].unique().tolist() == ["Base dos Dados"]
    assert normalized["source_table"].unique().tolist() == ["basedosdados.br_ms_populacao.municipio"]
    assert list(normalized.columns) == [
        "source_year",
        "ano",
        "cod_municipio",
        "id_municipio",
        "populacao_residente",
        "source",
        "source_table",
    ]
