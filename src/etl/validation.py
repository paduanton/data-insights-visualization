from __future__ import annotations

from src.etl.database import query_scalar


VALIDATION_CHECKS = {
    "SINAN/SIFCBR bruto": "SELECT COUNT(*) FROM bronze.sinan_sifilis_congenita",
    "SINASC bruto": "SELECT COUNT(*) FROM bronze.sinasc_nascidos_vivos",
    "SINAN Porto Alegre": (
        "SELECT COUNT(*) FROM silver.sinan_sifilis_congenita "
        "WHERE ano = 2024 AND cod_municipio_residencia = '431490'"
    ),
    "SINASC Porto Alegre": (
        "SELECT COUNT(*) FROM silver.sinasc_nascidos_vivos "
        "WHERE ano = 2024 AND cod_municipio_residencia = '431490'"
    ),
    "Maes negras sem pre-natal": (
        "SELECT COALESCE(SUM(casos_sc), 0) FROM gold.sinan_sc_sem_prenatal_escolaridade "
        "WHERE ano = 2024 AND cod_municipio_residencia = '431490' "
        "AND grupo_racial_mae = 'Maes negras'"
    ),
    "Maes nao negras sem pre-natal": (
        "SELECT COALESCE(SUM(casos_sc), 0) FROM gold.sinan_sc_sem_prenatal_escolaridade "
        "WHERE ano = 2024 AND cod_municipio_residencia = '431490' "
        "AND grupo_racial_mae = 'Maes nao negras'"
    ),
}

EXPECTED_2024 = {
    "SINAN/SIFCBR bruto": 12762,
    "SINASC bruto": 111988,
    "SINAN Porto Alegre": 137,
    "SINASC Porto Alegre": 12850,
    "Maes negras sem pre-natal": 10,
    "Maes nao negras sem pre-natal": 14,
}


def run_validation(engine, strict: bool) -> None:
    print("\nValidacao da carga")
    for label, sql in VALIDATION_CHECKS.items():
        value = int(query_scalar(engine, sql))
        print(f"- {label}: {value}")
        if strict and value != EXPECTED_2024[label]:
            raise AssertionError(f"{label}: esperado {EXPECTED_2024[label]}, obtido {value}")
