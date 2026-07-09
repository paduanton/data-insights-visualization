import pandas as pd

from src.etl.transform import (
    classify_racial_group,
    classify_sinan_prenatal,
    classify_sinan_schooling,
    normalize_columns,
    normalize_value,
)


def test_normalize_columns_handles_duplicates_and_empty_names():
    assert normalize_columns([" A ", "A", ""]) == ["a", "a_2", "coluna_sem_nome"]


def test_normalize_value_strips_blank_values():
    assert normalize_value("  texto  ") == "texto"
    assert normalize_value("   ") is None
    assert normalize_value(pd.NA) is None


def test_classify_racial_group_uses_black_as_pretas_and_pardas():
    assert classify_racial_group("2") == "Maes negras"
    assert classify_racial_group("4") == "Maes negras"
    assert classify_racial_group("1") == "Maes nao negras"
    assert classify_racial_group("5") == "Maes nao negras"
    assert classify_racial_group("9") == "Ignorado/sem informacao"


def test_classify_sinan_schooling_groups_years_of_study():
    assert classify_sinan_schooling("00") == "Ate 7 anos de estudo"
    assert classify_sinan_schooling("01") == "Ate 7 anos de estudo"
    assert classify_sinan_schooling("03") == "Ate 7 anos de estudo"
    assert classify_sinan_schooling("04") == "8 anos ou mais de estudo"
    assert classify_sinan_schooling("05") == "8 anos ou mais de estudo"
    assert classify_sinan_schooling("06") == "8 anos ou mais de estudo"
    assert classify_sinan_schooling("09") == "Ignorada/sem informacao"
    assert classify_sinan_schooling("10") == "Ignorada/sem informacao"


def test_classify_sinan_prenatal_categories():
    assert classify_sinan_prenatal("1") == "Com pre-natal"
    assert classify_sinan_prenatal("2") == "Sem pre-natal"
    assert classify_sinan_prenatal("9") == "Ignorado/sem informacao"
