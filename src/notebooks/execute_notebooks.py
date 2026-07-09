from __future__ import annotations

import argparse
import json
import os
import sys
import types
from pathlib import Path
from types import SimpleNamespace

from src.config import ROOT


DEFAULT_NOTEBOOKS = [
    "notebooks/analytics/00_validacao_ambiente_dados.ipynb",
    "notebooks/analytics/01_overview_sifilis_congenita.ipynb",
    "notebooks/analytics/02_auditoria_basedosdados.ipynb",
    "notebooks/analytics/03_prenatal_raca_escolaridade.ipynb",
    "notebooks/analytics/04_perfil_colunas_qualidade.ipynb",
    "notebooks/analytics/05_serie_historica_incidencia.ipynb",
    "notebooks/analytics/06_desigualdade_racial_incidencia.ipynb",
    "notebooks/analytics/07_diagnostico_tratamento_cuidado.ipynb",
    "notebooks/analytics/08_contexto_cnes_ibge_sim.ipynb",
    "notebooks/analytics/09_sintese_desigualdade_racial.ipynb",
    "notebooks/analytics/10_contexto_integrado_basedosdados.ipynb",
    "notebooks/11_analise_interseccional_desigualdade.ipynb",
    "notebooks/12_relatorio_final_consolidado.ipynb",
    "notebooks/visualizacao_sifilis_congenita_poars.ipynb",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Executa notebooks do projeto sem depender de Jupyter.")
    parser.add_argument(
        "notebooks",
        nargs="*",
        help="Caminhos dos notebooks a executar. Quando omitido, executa os notebooks analiticos documentados.",
    )
    return parser.parse_args()


def display(*objects: object, **_: object) -> None:
    for obj in objects:
        print(obj)


def get_ipython() -> None:
    return None


def execute_notebook(path: Path) -> None:
    os.environ.setdefault("MPLBACKEND", "Agg")
    os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".matplotlib"))
    (ROOT / ".matplotlib").mkdir(exist_ok=True)
    data = json.loads(path.read_text(encoding="utf-8"))
    module_name = f"notebook_{path.stem}"
    module = types.ModuleType(module_name)
    sys.modules[module_name] = module
    namespace = module.__dict__
    namespace.update(
        {
            "__name__": module_name,
            "__file__": str(path),
            "display": display,
            "get_ipython": get_ipython,
            "Image": lambda **kwargs: SimpleNamespace(**kwargs),
        }
    )
    os.chdir(ROOT)
    print(f"Executando {path}")
    for index, cell in enumerate(data.get("cells", []), start=1):
        if cell.get("cell_type") != "code":
            continue
        source = "".join(cell.get("source", []))
        if not source.strip():
            continue
        compiled = compile(source, f"{path}#cell-{index}", "exec")
        exec(compiled, namespace)


def main() -> None:
    args = parse_args()
    notebooks = args.notebooks or DEFAULT_NOTEBOOKS
    for notebook in notebooks:
        execute_notebook(ROOT / notebook)


if __name__ == "__main__":
    main()
