from __future__ import annotations

import argparse
import os
import shutil
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("MPLCONFIGDIR", str(Path(__file__).resolve().parents[2] / ".matplotlib"))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from sqlalchemy import create_engine, text

from src.config import DEFAULT_DATABASE_URL, ROOT, load_project_env, resolve_project_path


RESULTS_DIR = ROOT / "docs" / "assets" / "results"
FINAL_REPORT_DIR = ROOT / "outputs" / "images" / "final_report"
QUERY_DIR = ROOT / "database" / "queries"
PORTO_ALEGRE = "431490"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Gera imagens finais para o relatorio consolidado.")
    parser.add_argument("--database-url", default=None)
    parser.add_argument("--output-dir", default="outputs/images/final_report")
    return parser.parse_args()


def database_url(value: str | None) -> str:
    load_project_env()
    if value:
        return value
    import os

    return os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)


def read_sql_file(name: str) -> str:
    return (QUERY_DIR / name).read_text(encoding="utf-8")


def savefig(fig: plt.Figure, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)
    return path


def copy_existing(source_name: str, target_name: str, output_dir: Path) -> Path:
    target = output_dir / target_name
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(RESULTS_DIR / source_name, target)
    return target


def plot_incidence_by_group(engine, output_dir: Path) -> Path:
    data = pd.read_sql_query(text(read_sql_file("05_incidencia_por_grupo_racial.sql")), engine)
    labels = {"Maes negras": "Mães negras", "Maes nao negras": "Mães não negras"}
    colors = {"Maes negras": "#6F42C1", "Maes nao negras": "#0072B2"}

    fig, ax = plt.subplots(figsize=(10, 5))
    for group, subset in data.groupby("grupo_racial_mae"):
        subset = subset.sort_values("ano")
        ax.plot(
            subset["ano"],
            subset["incidencia_sc_por_1000_nv"],
            marker="o",
            linewidth=2.4,
            color=colors.get(group),
            label=labels.get(group, group),
        )
    ax.set_title("Incidência de sífilis congênita por grupo racial materno", fontsize=13, weight="bold")
    ax.set_xlabel("Ano")
    ax.set_ylabel("Casos por 1.000 nascidos vivos")
    ax.grid(alpha=0.25)
    ax.legend(title="Grupo racial materno", loc="upper center", bbox_to_anchor=(0.5, -0.16), ncol=2)
    fig.tight_layout(rect=[0, 0.08, 1, 1])
    return savefig(fig, output_dir / "incidencia_grupo_racial_ano.png")


def plot_ratio(engine, output_dir: Path) -> Path:
    data = pd.read_sql_query(text(read_sql_file("13_sintese_desigualdade_racial.sql")), engine)
    fig, ax = plt.subplots(figsize=(10, 4.8))
    ax.plot(
        data["ano"],
        data["razao_incidencia_negras_sobre_nao_negras"],
        color="#6F42C1",
        marker="o",
        linewidth=2.5,
    )
    ax.axhline(1, color="#6C757D", linestyle="--", linewidth=1.1)
    last = data.sort_values("ano").iloc[-1]
    ax.text(
        last["ano"] + 0.08,
        last["razao_incidencia_negras_sobre_nao_negras"],
        f"{last['razao_incidencia_negras_sobre_nao_negras']:.2f}x",
        va="center",
        fontsize=10,
        color="#6F42C1",
        weight="bold",
    )
    ax.set_title("Razão de incidência: mães negras sobre mães não negras", fontsize=13, weight="bold")
    ax.set_xlabel("Ano")
    ax.set_ylabel("Quantas vezes maior")
    ax.set_xlim(data["ano"].min() - 0.2, data["ano"].max() + 0.8)
    ax.grid(alpha=0.25)
    fig.tight_layout()
    return savefig(fig, output_dir / "razao_incidencia_racial.png")


def plot_detailed_race(engine, output_dir: Path) -> Path:
    data = pd.read_sql_query(text(read_sql_file("16_incidencia_raca_cor_detalhada.sql")), engine)
    stable_order = ["Branca", "Preta", "Parda"]
    unstable_order = ["Amarela", "Indigena", "Ignorada"]
    label_map = {"Indigena": "Indígena", "Ignorada": "Ignorada"}
    colors = {
        "Branca": "#0072B2",
        "Preta": "#6F42C1",
        "Parda": "#D55E00",
    }
    fig, ax = plt.subplots(figsize=(11.5, 5.4))
    for race in stable_order:
        subset = data[data["raca_cor_mae"].eq(race)].sort_values("ano")
        if subset.empty:
            continue
        ax.plot(
            subset["ano"],
            subset["incidencia_sc_por_1000_nv"],
            marker="o",
            linewidth=2.4,
            color=colors[race],
            label=race,
        )

    unstable_lines = []
    for race in unstable_order:
        subset = data[data["raca_cor_mae"].eq(race)]
        if subset.empty:
            continue
        low_years = int(subset[subset["nascidos_vivos"] < 30]["ano"].nunique())
        total_cases = int(subset["casos_sc"].sum())
        total_births = int(subset["nascidos_vivos"].sum())
        unstable_lines.append(
            f"{label_map.get(race, race)}: {total_cases} casos, {total_births} NV; "
            f"{low_years} anos com denominador < 30"
        )

    ax.set_title("Incidência por raça/cor materna detalhada", fontsize=13, weight="bold")
    ax.set_xlabel("Ano")
    ax.set_ylabel("Casos por 1.000 nascidos vivos")
    ax.grid(alpha=0.25)
    ax.legend(title="Raça/cor materna", loc="upper center", bbox_to_anchor=(0.5, -0.16), ncol=3)
    fig.text(
        0.5,
        0.02,
        "Categorias com denominador instável não entram na linha principal: " + " | ".join(unstable_lines),
        ha="center",
        fontsize=8.5,
        color="#333333",
    )
    fig.tight_layout(rect=[0, 0.12, 1, 1])
    return savefig(fig, output_dir / "incidencia_raca_cor_detalhada.png")


def plot_prenatal(engine, output_dir: Path) -> Path:
    data = pd.read_sql_query(text(read_sql_file("06_prenatal_por_grupo_racial.sql")), engine)
    data = data[data["realizacao_prenatal"].eq("Sem pre-natal")].copy()
    labels = {"Maes negras": "Mães negras", "Maes nao negras": "Mães não negras"}
    colors = {"Maes negras": "#6F42C1", "Maes nao negras": "#0072B2"}
    fig, ax = plt.subplots(figsize=(10, 4.8))
    for group, subset in data.groupby("grupo_racial_mae"):
        subset = subset.sort_values("ano")
        ax.plot(
            subset["ano"],
            subset["percentual_no_group" if "percentual_no_group" in subset else "percentual_no_grupo"],
            marker="o",
            linewidth=2.3,
            color=colors.get(group),
            label=labels.get(group, group),
        )
    ax.set_title("Casos sem pré-natal por grupo racial materno", fontsize=13, weight="bold")
    ax.set_xlabel("Ano")
    ax.set_ylabel("Percentual dos casos no grupo")
    ax.grid(alpha=0.25)
    ax.legend(title="Grupo racial materno", loc="upper center", bbox_to_anchor=(0.5, -0.16), ncol=2)
    fig.tight_layout(rect=[0, 0.08, 1, 1])
    return savefig(fig, output_dir / "prenatal_grupo_racial.png")


def plot_schooling_without_prenatal(engine, output_dir: Path) -> Path:
    query = """
    SELECT
        grupo_racial_mae,
        escolaridade_mae,
        SUM(casos_sc)::integer AS casos
    FROM gold.sinan_sc_sem_prenatal_escolaridade
    WHERE cod_municipio_residencia = '431490'
      AND grupo_racial_mae IN ('Maes negras', 'Maes nao negras')
    GROUP BY grupo_racial_mae, escolaridade_mae
    """
    data = pd.read_sql_query(text(query), engine)
    group_order = ["Maes nao negras", "Maes negras"]
    schooling_order = ["Ate 7 anos de estudo", "8 anos ou mais de estudo", "Ignorada/sem informacao"]
    group_labels = {
        "Maes nao negras": "Mães não negras",
        "Maes negras": "Mães negras",
    }
    schooling_labels = {
        "Ate 7 anos de estudo": "Até 7 anos de estudo",
        "8 anos ou mais de estudo": "8 anos ou mais de estudo",
        "Ignorada/sem informacao": "Ignorada/sem informação",
    }
    colors = {
        "Ate 7 anos de estudo": "#D55E00",
        "8 anos ou mais de estudo": "#0072B2",
        "Ignorada/sem informacao": "#8A8F98",
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

    fig, ax = plt.subplots(figsize=(11.2, 5.2))
    left = {group: 0.0 for group in group_order}
    y_positions = list(range(len(group_order)))
    for schooling in schooling_order:
        subset = plot_data[plot_data["escolaridade_mae"].eq(schooling)]
        widths = subset["percentual"].tolist()
        starts = [left[group] for group in group_order]
        bars = ax.barh(
            y_positions,
            widths,
            left=starts,
            color=colors[schooling],
            edgecolor="white",
            linewidth=0.9,
            label=schooling_labels[schooling],
            height=0.48,
        )
        for group, start, width, cases, bar in zip(group_order, starts, widths, subset["casos"], bars, strict=True):
            if cases > 0 and width >= 8:
                ax.text(
                    start + width / 2,
                    bar.get_y() + bar.get_height() / 2,
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
        ax.text(101, y_positions[group_order.index(group)], f"Total: {total}", va="center", fontsize=9.5, color="#333333")

    ax.set_title(
        "Casos de sífilis congênita sem pré-natal: escolaridade por grupo racial (2015-2024)",
        fontsize=13,
        weight="bold",
    )
    ax.set_xlabel("Distribuição percentual dentro dos casos sem pré-natal")
    ax.set_yticks(y_positions, [group_labels[group] for group in group_order])
    ax.set_xlim(0, 112)
    ax.grid(axis="x", alpha=0.25)
    ax.legend(title="Escolaridade materna", loc="upper center", bbox_to_anchor=(0.5, -0.16), ncol=3)
    fig.tight_layout(rect=[0, 0.08, 1, 1])

    docs_output = savefig(fig, RESULTS_DIR / "escolaridade_sem_prenatal_grupo_racial.png")
    target = output_dir / "escolaridade_sem_prenatal_grupo_racial.png"
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(docs_output, target)
    return target


def plot_black_mothers_profile(engine, output_dir: Path) -> Path:
    data = pd.read_sql_query(text(read_sql_file("18_perfil_maes_negras_escolaridade_idade.sql")), engine)
    schooling_order = ["Ate 7 anos de estudo", "8 anos ou mais de estudo", "Ignorada/sem informacao"]
    age_order = ["Ate 19 anos", "20 a 29 anos", "30 a 39 anos", "40 anos ou mais", "Ignorada/sem informacao"]
    labels_schooling = {
        "Ate 7 anos de estudo": "Até 7 anos",
        "8 anos ou mais de estudo": "8 anos ou mais",
        "Ignorada/sem informacao": "Ignorada",
    }
    labels_age = {
        "Ate 19 anos": "Até 19",
        "20 a 29 anos": "20 a 29",
        "30 a 39 anos": "30 a 39",
        "40 anos ou mais": "40+",
        "Ignorada/sem informacao": "Ignorada",
    }
    table = (
        data.pivot_table(index="escolaridade_mae", columns="faixa_etaria_mae", values="casos_sc", fill_value=0)
        .reindex(index=schooling_order, columns=age_order, fill_value=0)
    )
    fig, ax = plt.subplots(figsize=(10, 4.8))
    im = ax.imshow(table.values, cmap="Purples")
    ax.set_xticks(range(len(age_order)), [labels_age[item] for item in age_order])
    ax.set_yticks(range(len(schooling_order)), [labels_schooling[item] for item in schooling_order])
    for row in range(table.shape[0]):
        for col in range(table.shape[1]):
            value = int(table.iloc[row, col])
            ax.text(col, row, str(value), ha="center", va="center", color="white" if value > table.values.max() * 0.55 else "#222222")
    ax.set_title("Mães negras: escolaridade e faixa etária nos casos notificados", fontsize=13, weight="bold")
    ax.set_xlabel("Faixa etária materna")
    ax.set_ylabel("Escolaridade materna")
    fig.colorbar(im, ax=ax, fraction=0.035, pad=0.03, label="Casos")
    fig.tight_layout()
    return savefig(fig, output_dir / "perfil_maes_negras_escolaridade_idade.png")


def plot_intersectional(engine, output_dir: Path) -> Path:
    data_all = pd.read_sql_query(text(read_sql_file("17_analise_interseccional_desigualdade.sql")), engine)
    totals = data_all.groupby("grupo_racial_mae")["casos_sc"].sum().to_dict()
    data = data_all[data_all["marcador_vulnerabilidade"].eq("Maior vulnerabilidade registrada")].copy()
    labels = {"Maes negras": "Mães negras", "Maes nao negras": "Mães não negras"}
    data["grupo"] = data["grupo_racial_mae"].map(labels)
    data["total_grupo"] = data["grupo_racial_mae"].map(totals).astype(int)

    fig, ax = plt.subplots(figsize=(8.8, 4.8))
    bars = ax.barh(
        data["grupo"],
        data["percentual_no_grupo"],
        color=["#6F42C1" if group == "Maes negras" else "#0072B2" for group in data["grupo_racial_mae"]],
    )
    for bar, row in zip(bars, data.itertuples(index=False)):
        ax.text(
            bar.get_width() + 0.8,
            bar.get_y() + bar.get_height() / 2,
            f"{row.percentual_no_grupo:.1f}% (n={int(row.casos_sc)} de {int(row.total_grupo)})",
            va="center",
            fontsize=10,
        )
    ax.set_title("Marcadores combinados de vulnerabilidade por grupo racial", fontsize=13, weight="bold")
    ax.set_xlabel("Percentual dos casos no grupo")
    ax.set_xlim(0, min(100, max(data["percentual_no_grupo"]) + 15))
    ax.grid(axis="x", alpha=0.25)
    fig.text(
        0.5,
        0.02,
        "Critério: baixa/ignorada escolaridade e pelo menos um marcador de cuidado ausente, tardio, inadequado ou ignorado.",
        ha="center",
        fontsize=9,
        color="#333333",
    )
    fig.tight_layout(rect=[0, 0.08, 1, 1])
    return savefig(fig, output_dir / "analise_interseccional_desigualdade.png")


def plot_quality(engine, output_dir: Path) -> Path:
    query = """
    SELECT
        base,
        variavel,
        SUM(ignorados) AS ignorados,
        SUM(total) AS total,
        ROUND(SUM(ignorados)::numeric / NULLIF(SUM(total), 0) * 100, 2) AS percentual_ignorado
    FROM gold.qualidade_registros
    WHERE cod_municipio_residencia = '431490'
    GROUP BY base, variavel
    ORDER BY percentual_ignorado DESC
    """
    data = pd.read_sql_query(text(query), engine)
    data["label"] = data["base"] + " | " + data["variavel"]
    fig, ax = plt.subplots(figsize=(10, 5.2))
    bars = ax.barh(data["label"], data["percentual_ignorado"], color="#8A8F98")
    for bar, value in zip(bars, data["percentual_ignorado"]):
        ax.text(bar.get_width() + 0.4, bar.get_y() + bar.get_height() / 2, f"{value:.1f}%", va="center", fontsize=9)
    ax.set_title("Percentual de registros ignorados por variável crítica", fontsize=13, weight="bold")
    ax.set_xlabel("Percentual ignorado")
    ax.invert_yaxis()
    ax.grid(axis="x", alpha=0.25)
    fig.tight_layout()
    return savefig(fig, output_dir / "qualidade_dados_ignorados.png")


def generate_all(database_url_value: str | None = None, output_dir_value: str | Path = FINAL_REPORT_DIR) -> list[Path]:
    output_dir = resolve_project_path(output_dir_value)
    output_dir.mkdir(parents=True, exist_ok=True)
    engine = create_engine(database_url(database_url_value))
    generated = [
        plot_incidence_by_group(engine, output_dir),
        plot_ratio(engine, output_dir),
        plot_detailed_race(engine, output_dir),
        plot_prenatal(engine, output_dir),
        plot_schooling_without_prenatal(engine, output_dir),
        copy_existing("diagnostico_materno_grupo_racial.png", "diagnostico_materno_grupo_racial.png", output_dir),
        copy_existing("tratamento_materno_grupo_racial.png", "tratamento_materno_grupo_racial.png", output_dir),
        plot_black_mothers_profile(engine, output_dir),
        plot_intersectional(engine, output_dir),
        plot_quality(engine, output_dir),
    ]
    return generated


def main() -> None:
    args = parse_args()
    for path in generate_all(args.database_url, args.output_dir):
        print(path.relative_to(ROOT))


if __name__ == "__main__":
    main()
