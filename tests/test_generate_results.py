import pandas as pd

from src.visualization import generate_results
from src.visualization.generate_results import save_basedosdados_periods, save_maternal_treatment


def test_save_basedosdados_periods_creates_png(tmp_path):
    audit_csv = tmp_path / "basedosdados_audit.csv"
    pd.DataFrame(
        [
            {"table": "basedosdados.br_ms_sinasc.microdados", "available_period": "1996-2024"},
            {"table": "basedosdados.br_ms_sim.microdados", "available_period": "1996-2024"},
            {"table": "basedosdados.br_ms_cnes.estabelecimento", "available_period": "2005-2026"},
        ]
    ).to_csv(audit_csv, index=False)

    output = save_basedosdados_periods(audit_csv, tmp_path)

    assert output.name == "auditoria_basedosdados_periodos.png"
    assert output.exists()
    assert output.stat().st_size > 0


def test_save_maternal_treatment_creates_png(monkeypatch, tmp_path):
    data = pd.DataFrame(
        [
            {"ano": 2023, "grupo_racial_mae": "Maes negras", "tratamento_materno_adequado": "Inadequado", "casos": 10},
            {"ano": 2023, "grupo_racial_mae": "Maes negras", "tratamento_materno_adequado": "Adequado", "casos": 5},
            {
                "ano": 2023,
                "grupo_racial_mae": "Maes nao negras",
                "tratamento_materno_adequado": "Inadequado",
                "casos": 8,
            },
            {
                "ano": 2023,
                "grupo_racial_mae": "Maes nao negras",
                "tratamento_materno_adequado": "Adequado",
                "casos": 12,
            },
            {"ano": 2024, "grupo_racial_mae": "Maes negras", "tratamento_materno_adequado": "Inadequado", "casos": 14},
            {"ano": 2024, "grupo_racial_mae": "Maes negras", "tratamento_materno_adequado": "Adequado", "casos": 1},
            {
                "ano": 2024,
                "grupo_racial_mae": "Maes nao negras",
                "tratamento_materno_adequado": "Inadequado",
                "casos": 9,
            },
            {
                "ano": 2024,
                "grupo_racial_mae": "Maes nao negras",
                "tratamento_materno_adequado": "Adequado",
                "casos": 3,
            },
        ]
    )

    monkeypatch.setattr(generate_results, "create_engine", lambda database_url: object())
    monkeypatch.setattr(generate_results.pd, "read_sql_query", lambda query, engine: data)

    output = save_maternal_treatment("postgresql://example", tmp_path)

    assert output.name == "tratamento_materno_grupo_racial.png"
    assert output.exists()
    assert output.stat().st_size > 0
