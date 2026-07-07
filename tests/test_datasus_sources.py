from src.etl.datasus_sources import parse_years, resolve_datasus_sources


def test_parse_years_accepts_single_year_default():
    assert parse_years(2024, None) == [2024]


def test_parse_years_accepts_range():
    assert parse_years(None, "2021:2024") == [2021, 2022, 2023, 2024]


def test_parse_years_accepts_comma_list_sorted_unique():
    assert parse_years(None, "2024,2022,2024") == [2022, 2024]


def test_resolve_datasus_sources_uses_current_2024_paths():
    pairs, missing = resolve_datasus_sources(
        [2024],
        sinan="data/raw/SIFCBR24.dbc",
        sinasc="data/raw/sinasc/DNRS2024.dbc",
    )

    assert missing == []
    assert len(pairs) == 1
    assert pairs[0].year == 2024
    assert pairs[0].sinan.name == "SIFCBR24.dbc"
    assert pairs[0].sinasc.name == "DNRS2024.dbc"


def test_resolve_datasus_sources_reports_missing_years():
    pairs, missing = resolve_datasus_sources([2014])

    assert pairs == []
    assert any("SINAN/SIFCBR 2014" in item for item in missing)
    assert any("SINASC 2014" in item for item in missing)
