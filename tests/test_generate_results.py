import pandas as pd

from src.visualization.generate_results import save_basedosdados_periods


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
