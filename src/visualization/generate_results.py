from __future__ import annotations

import argparse
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", str(Path(".matplotlib").resolve()))

import matplotlib
import pandas as pd
from sqlalchemy import create_engine, text

from src.config import DEFAULT_DATABASE_URL, ROOT, resolve_project_path


matplotlib.use("Agg")
import matplotlib.pyplot as plt

RESULTS_DIR = ROOT / "docs/assets/results"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Gera figuras finais a partir dos resultados analiticos.")
    parser.add_argument(
        "--database-url",
        default=DEFAULT_DATABASE_URL,
        help="URL SQLAlchemy do PostgreSQL.",
    )
    parser.add_argument(
        "--audit-csv",
        default="data/profiles/basedosdados_audit.csv",
        help="CSV de auditoria da Base dos Dados.",
    )
    parser.add_argument(
        "--output-dir",
        default="docs/assets/results",
        help="Diretorio de saida das imagens.",
    )
    return parser.parse_args()


def save_lab_schooling_without_prenatal(database_url: str) -> Path:
    output_dir = ROOT / "outputs/images/graphs"
    output_dir.mkdir(parents=True, exist_ok=True)
    engine = create_engine(database_url)
    query = """
SELECT
    grupo_racial_mae,
    escolaridade_mae,
    SUM(casos_sc)::integer AS casos
FROM gold.sinan_sc_sem_prenatal_escolaridade
WHERE ano = 2024
  AND cod_municipio_residencia = '431490'
  AND grupo_racial_mae IN ('Maes negras', 'Maes nao negras')
GROUP BY grupo_racial_mae, escolaridade_mae
""".strip()
    data = pd.read_sql_query(text(query), engine)

    group_order = ["Maes negras", "Maes nao negras"]
    schooling_order = ["Ate 7 anos de estudo", "8 anos ou mais de estudo", "Ignorada/sem informacao"]
    display_group = {
        "Maes negras": "Mães negras",
        "Maes nao negras": "Mães não negras",
    }
    display_schooling = {
        "Ate 7 anos de estudo": "Até 7 anos de estudo",
        "8 anos ou mais de estudo": "8 anos ou mais de estudo",
        "Ignorada/sem informacao": "Ignorada/sem informação",
    }
    base = pd.MultiIndex.from_product(
        [group_order, schooling_order],
        names=["grupo_racial_mae", "escolaridade_mae"],
    ).to_frame(index=False)
    plot_data = base.merge(data, on=["grupo_racial_mae", "escolaridade_mae"], how="left").fillna({"casos": 0})
    plot_data["casos"] = plot_data["casos"].astype(int)
    plot_data["total_grupo"] = plot_data.groupby("grupo_racial_mae")["casos"].transform("sum")
    plot_data["percentual"] = plot_data.apply(
        lambda row: 0 if row.total_grupo == 0 else row.casos / row.total_grupo * 100,
        axis=1,
    )

    fig, ax = plt.subplots(figsize=(10, 5.2))
    colors = {
        "Ate 7 anos de estudo": "#D55E00",
        "8 anos ou mais de estudo": "#0072B2",
        "Ignorada/sem informacao": "#8A8F98",
    }
    left = {group: 0.0 for group in group_order}
    y_positions = list(range(len(group_order)))
    y_labels = [display_group[group] for group in group_order]
    for schooling in schooling_order:
        subset = plot_data[plot_data["escolaridade_mae"].eq(schooling)]
        widths = subset["percentual"].tolist()
        starts = [left[group] for group in group_order]
        ax.barh(
            y_positions,
            widths,
            left=starts,
            color=colors[schooling],
            edgecolor="white",
            label=display_schooling[schooling],
            height=0.48,
        )
        for group, start, width, cases in zip(group_order, starts, widths, subset["casos"], strict=True):
            if cases > 0 and width >= 8:
                ax.text(
                    start + width / 2,
                    y_positions[group_order.index(group)],
                    f"{width:.1f}%\n(n={cases})",
                    ha="center",
                    va="center",
                    color="white",
                    fontsize=9,
                    weight="bold",
                )
            left[group] += width

    for group in group_order:
        total = int(plot_data.loc[plot_data["grupo_racial_mae"].eq(group), "casos"].sum())
        ax.text(101, y_positions[group_order.index(group)], f"Total: {total}", va="center", fontsize=9, color="#333333")

    ax.set_xlim(0, 112)
    ax.set_yticks(y_positions)
    ax.set_yticklabels(y_labels)
    ax.set_xlabel("Distribuição percentual dentro dos casos sem pré-natal")
    ax.set_title("Casos de sífilis congênita sem pré-natal: escolaridade por grupo racial", fontsize=14, weight="bold")
    ax.grid(axis="x", color="#E6E6E6")
    ax.legend(title="Escolaridade materna", loc="lower center", bbox_to_anchor=(0.5, -0.32), ncol=3, frameon=True)
    fig.tight_layout()

    output = output_dir / "visualizacao_sifilis_congenita_poars_escolaridade_sem_prenatal.png"
    fig.savefig(output, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return output


def save_environment_validation(database_url: str, output_dir: Path) -> Path:
    engine = create_engine(database_url)
    query = """
SELECT 'SINAN RS 2024' AS indicador, COUNT(*)::integer AS valor
FROM bronze.sinan_sifilis_congenita
WHERE source_year = '2024'
UNION ALL
SELECT 'SINASC RS 2024', COUNT(*)::integer
FROM bronze.sinasc_nascidos_vivos
WHERE source_year = '2024'
UNION ALL
SELECT 'SINAN Porto Alegre 2024', COUNT(*)::integer
FROM silver.sinan_sifilis_congenita
WHERE ano = 2024 AND cod_municipio_residencia = '431490'
UNION ALL
SELECT 'SINASC Porto Alegre 2024', COUNT(*)::integer
FROM silver.sinasc_nascidos_vivos
WHERE ano = 2024 AND cod_municipio_residencia = '431490'
""".strip()
    data = pd.read_sql_query(text(query), engine)

    fig, ax = plt.subplots(figsize=(9.5, 4.8))
    colors = ["#006BA4", "#8F9DA8", "#B02A37", "#D55E00"]
    bars = ax.barh(data["indicador"], data["valor"], color=colors)
    ax.set_title("Validação da carga 2024", fontsize=14, weight="bold")
    ax.set_xlabel("Registros")
    ax.grid(axis="x", color="#E6E6E6")
    ax.bar_label(bars, labels=[f"{value:,}".replace(",", ".") for value in data["valor"]], padding=4)
    fig.tight_layout()

    output = output_dir / "validacao_ambiente_dados.png"
    fig.savefig(output, dpi=160)
    plt.close(fig)
    return output


def save_overview(database_url: str, output_dir: Path) -> Path:
    engine = create_engine(database_url)
    query = """
SELECT ano, casos_sc, nascidos_vivos, incidencia_sc_por_1000_nv
FROM gold.indicadores_municipio_ano
WHERE cod_municipio_residencia = '431490'
ORDER BY ano
""".strip()
    data = pd.read_sql_query(text(query), engine)

    fig, ax1 = plt.subplots(figsize=(10, 5.2))
    ax1.bar(data["ano"], data["casos_sc"], color="#8F9DA8", label="Casos notificados")
    ax1.set_ylabel("Casos notificados")
    ax1.grid(axis="y", color="#E6E6E6")

    ax2 = ax1.twinx()
    ax2.plot(
        data["ano"],
        data["incidencia_sc_por_1000_nv"],
        marker="o",
        color="#006BA4",
        linewidth=2.4,
        label="Incidencia por 1.000 nascidos vivos",
    )
    ax2.set_ylabel("Casos por 1.000 nascidos vivos")
    ax1.set_xlabel("Ano")
    fig.suptitle("Porto Alegre: casos e incidencia de sifilis congenita", fontsize=14, weight="bold")
    bars, labels1 = ax1.get_legend_handles_labels()
    lines, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(bars + lines, labels1 + labels2, loc="upper right", frameon=True)
    fig.tight_layout()

    output = output_dir / "overview_sifilis_congenita.png"
    fig.savefig(output, dpi=160)
    plt.close(fig)
    return output


def save_prenatal_race_schooling(database_url: str, output_dir: Path) -> Path:
    engine = create_engine(database_url)
    query = """
SELECT
    grupo_racial_mae,
    realizacao_prenatal,
    escolaridade_mae,
    COUNT(*)::integer AS casos
FROM silver.sinan_sifilis_congenita
WHERE ano = 2024
  AND cod_municipio_residencia = '431490'
  AND grupo_racial_mae IN ('Maes negras', 'Maes nao negras')
GROUP BY grupo_racial_mae, realizacao_prenatal, escolaridade_mae
""".strip()
    data = pd.read_sql_query(text(query), engine)
    data["dimensao"] = data["grupo_racial_mae"] + " | " + data["realizacao_prenatal"]
    pivot = data.pivot_table(
        index="dimensao",
        columns="escolaridade_mae",
        values="casos",
        aggfunc="sum",
        fill_value=0,
    )
    order = [
        "Maes negras | Sem pre-natal",
        "Maes nao negras | Sem pre-natal",
        "Maes negras | Com pre-natal",
        "Maes nao negras | Com pre-natal",
    ]
    columns = ["Ate 7 anos de estudo", "8 anos ou mais de estudo", "Ignorada/sem informacao"]
    pivot = pivot.reindex(order).fillna(0)
    for column in columns:
        if column not in pivot.columns:
            pivot[column] = 0
    pivot = pivot[columns]
    row_labels = {
        "Maes negras | Sem pre-natal": "Mães negras | Sem pré-natal",
        "Maes nao negras | Sem pre-natal": "Mães não negras | Sem pré-natal",
        "Maes negras | Com pre-natal": "Mães negras | Com pré-natal",
        "Maes nao negras | Com pre-natal": "Mães não negras | Com pré-natal",
    }
    column_labels = {
        "Ate 7 anos de estudo": "Até 7 anos de estudo",
        "8 anos ou mais de estudo": "8 anos ou mais de estudo",
        "Ignorada/sem informacao": "Ignorada/sem informação",
    }

    fig, ax = plt.subplots(figsize=(10, 5.6))
    colors = {
        "Ate 7 anos de estudo": "#D55E00",
        "8 anos ou mais de estudo": "#0072B2",
        "Ignorada/sem informacao": "#8A8F98",
    }
    left = pd.Series(0, index=pivot.index, dtype=float)
    for column in columns:
        ax.barh(
            range(len(pivot.index)),
            pivot[column],
            left=left,
            color=colors[column],
            edgecolor="white",
            label=column_labels[column],
        )
        left += pivot[column]
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels([row_labels[index] for index in pivot.index])
    ax.set_title("Porto Alegre 2024: pré-natal, raça/cor e escolaridade materna", fontsize=14, weight="bold")
    ax.set_xlabel("Casos notificados")
    ax.grid(axis="x", color="#E6E6E6")
    ax.legend(title="Escolaridade", loc="lower center", bbox_to_anchor=(0.5, -0.32), ncol=3, frameon=True)
    fig.tight_layout()

    output = output_dir / "prenatal_raca_escolaridade.png"
    fig.savefig(output, dpi=160, bbox_inches="tight")
    plt.close(fig)
    return output


def save_basedosdados_periods(audit_csv: Path, output_dir: Path) -> Path:
    audit = pd.read_csv(audit_csv)
    audit[["ano_min", "ano_max"]] = audit["available_period"].str.split("-", expand=True).astype(int)
    labels = {
        "basedosdados.br_ms_sinasc.microdados": "SINASC",
        "basedosdados.br_ms_sim.microdados": "SIM",
        "basedosdados.br_ms_cnes.estabelecimento": "CNES",
        "basedosdados.br_ms_populacao.municipio": "Populacao",
        "basedosdados.br_ms_sih.servicos_profissionais": "SIH",
        "basedosdados.br_ms_sinan.microdados_violencia": "SINAN violencia",
    }
    audit["label"] = audit["table"].map(labels).fillna(audit["table"])
    audit = audit.sort_values("ano_min")

    fig, ax = plt.subplots(figsize=(10, 4.8))
    colors = ["#006BA4", "#FF800E", "#ABABAB", "#595959", "#5F9ED1", "#C85200"]
    y_positions = list(range(len(audit)))
    for idx, (_, row) in enumerate(audit.iterrows()):
        ax.barh(
            y_positions[idx],
            row["ano_max"] - row["ano_min"] + 1,
            left=row["ano_min"],
            color=colors[idx % len(colors)],
            height=0.55,
        )
        ax.text(row["ano_min"] - 0.4, y_positions[idx], str(row["ano_min"]), va="center", ha="right", fontsize=9)
        ax.text(row["ano_max"] + 0.4, y_positions[idx], str(row["ano_max"]), va="center", ha="left", fontsize=9)

    ax.axvspan(2015, 2024, color="#D9EAD3", alpha=0.45)
    ax.set_title(
        "Cobertura temporal auditada na Base dos Dados\nFaixa verde: recorte usado no projeto (2015-2024)",
        fontsize=13,
        weight="bold",
    )
    ax.set_xlabel("Ano disponivel")
    ax.set_ylabel("Tabela auditada")
    ax.set_yticks(y_positions)
    ax.set_yticklabels(audit["label"])
    ax.set_xlim(audit["ano_min"].min() - 3, audit["ano_max"].max() + 3)
    ax.grid(axis="x", color="#E6E6E6")
    fig.tight_layout()

    output = output_dir / "auditoria_basedosdados_periodos.png"
    fig.savefig(output, dpi=160)
    plt.close(fig)
    return output


def save_integrated_context(database_url: str, output_dir: Path) -> Path:
    query = (ROOT / "database/queries/14_contexto_integrado_municipio.sql").read_text(encoding="utf-8")
    engine = create_engine(database_url)
    contexto = pd.read_sql_query(text(query), engine)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6.2), sharex=True, height_ratios=[2, 1.3])
    ax1.plot(
        contexto["ano"],
        contexto["incidencia_sc_por_1000_nv"],
        marker="o",
        color="#006BA4",
        linewidth=2.5,
        label="Incidencia por 1.000 nascidos vivos",
    )
    ax1.set_ylabel("Casos por 1.000 nascidos vivos")
    ax1.grid(axis="y", color="#E6E6E6")
    ax1.legend(loc="upper right", frameon=True)

    ax2.bar(
        contexto["ano"],
        contexto["estabelecimentos_distintos"],
        color="#8F9DA8",
        label="Estabelecimentos CNES distintos em dezembro",
    )
    ax2.set_ylabel("Estabelecimentos CNES")
    ax2.set_xlabel("Ano")
    ax2.grid(axis="y", color="#E6E6E6")
    ax2.legend(loc="upper left", frameon=True)

    fig.suptitle("Porto Alegre: incidencia de sifilis congenita e contexto assistencial", fontsize=14, weight="bold")
    fig.tight_layout()

    output = output_dir / "contexto_integrado_basedosdados.png"
    fig.savefig(output, dpi=160)
    plt.close(fig)
    return output


def main() -> None:
    args = parse_args()
    output_dir = resolve_project_path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    generated = [
        save_lab_schooling_without_prenatal(args.database_url),
        save_environment_validation(args.database_url, output_dir),
        save_overview(args.database_url, output_dir),
        save_prenatal_race_schooling(args.database_url, output_dir),
        save_basedosdados_periods(resolve_project_path(args.audit_csv), output_dir),
        save_integrated_context(args.database_url, output_dir),
    ]
    for output in generated:
        print(output.relative_to(ROOT))


if __name__ == "__main__":
    main()
