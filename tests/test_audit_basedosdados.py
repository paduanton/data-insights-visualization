from src.etl.audit_basedosdados import (
    BasedosdadosTable,
    columns_sql,
    first_existing,
    period_sql,
    tables_from_env,
    year_series_sql,
)


def test_first_existing_returns_first_matching_candidate():
    columns = {"id_municipio", "ano", "sigla_uf"}

    assert first_existing(columns, ["ano_obito", "ano"]) == "ano"


def test_columns_sql_uses_information_schema_for_dataset():
    table = BasedosdadosTable("basedosdados.br_ms_sinasc.microdados", "uso", "validar")

    sql = columns_sql(table)

    assert "`basedosdados.br_ms_sinasc.INFORMATION_SCHEMA.COLUMNS`" in sql
    assert "table_name = 'microdados'" in sql


def test_period_sql_filters_rs_when_uf_column_exists():
    table = BasedosdadosTable("basedosdados.br_ms_sinasc.microdados", "uso", "validar")

    sql, year_column, municipality_column = period_sql(table, {"ano", "sigla_uf", "id_municipio_residencia"})

    assert year_column == "ano"
    assert municipality_column == "id_municipio_residencia"
    assert "sigla_uf = 'RS'" in sql
    assert "MIN(ano)" in sql


def test_year_series_sql_groups_by_year_and_filters_rs():
    table = BasedosdadosTable("basedosdados.br_ms_sim.microdados", "uso", "validar")

    sql = year_series_sql(table, "ano", {"ano", "sigla_uf"})

    assert "GROUP BY ano" in sql
    assert "ORDER BY ano" in sql
    assert "sigla_uf = 'RS'" in sql


def test_tables_from_env_uses_configured_table_id(monkeypatch):
    monkeypatch.setenv("BASEDOSDADOS_SINASC_TABLE", "basedosdados.br_ms_sinasc.microdados_teste")

    tables = tables_from_env()

    assert tables[0].table == "basedosdados.br_ms_sinasc.microdados_teste"
    assert any(table.table == "basedosdados.br_ms_sim.microdados" for table in tables)
