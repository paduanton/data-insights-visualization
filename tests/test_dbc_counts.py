from pathlib import Path

from src.etl.dbc import read_dbc


def test_dbc_sources_have_expected_2024_counts():
    sinan = read_dbc(Path("data/raw/SIFCBR24.dbc"))
    sinasc = read_dbc(Path("data/raw/sinasc/DNRS2024.dbc"))

    assert sinan.shape == (12762, 64)
    assert sinasc.shape == (111988, 61)


def test_porto_alegre_subset_counts_match_validated_baseline():
    sinan = read_dbc(Path("data/raw/SIFCBR24.dbc"))
    sinasc = read_dbc(Path("data/raw/sinasc/DNRS2024.dbc"))

    sinan_poa = sinan[sinan["ID_MN_RESI"].astype(str).str.strip().str.startswith("431490")]
    sinasc_poa = sinasc[sinasc["CODMUNRES"].astype(str).str.strip().str.startswith("431490")]

    assert len(sinan_poa) == 137
    assert len(sinasc_poa) == 12850
