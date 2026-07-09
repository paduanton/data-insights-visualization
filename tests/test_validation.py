from src.etl.validation import VALIDATION_CHECKS


def test_strict_raw_counts_are_scoped_to_2024_baseline():
    assert "source_year = '2024'" in VALIDATION_CHECKS["SINAN/SIFCBR bruto"]
    assert "source_year = '2024'" in VALIDATION_CHECKS["SINASC bruto"]
