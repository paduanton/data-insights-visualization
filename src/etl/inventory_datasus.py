from __future__ import annotations

import argparse
import csv
import re
import zipfile
from dataclasses import asdict, dataclass
from pathlib import Path

from src.config import ROOT, resolve_project_path
from src.etl.datasus_sources import (
    default_cnes_st_candidates,
    default_sim_do_candidates,
    default_sinan_candidates,
    default_sinasc_candidates,
    first_existing,
    parse_years,
)


@dataclass(frozen=True)
class InventoryRow:
    source: str
    year: int
    expected_kind: str
    priority: str
    expected_file: str
    status: str
    path: str
    target_path: str
    official_url: str
    source_hint: str


@dataclass(frozen=True)
class FileInventoryRow:
    base: str
    arquivo: str
    ano: str
    uf: str
    tipo: str
    formato: str
    status: str
    caminho: str
    observacoes: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Inventaria arquivos DATASUS esperados antes da consolidacao historica."
    )
    parser.add_argument("--year", type=int, default=2024, help="Ano de referencia quando --years nao for usado.")
    parser.add_argument("--years", help="Anos a inventariar. Aceita lista '2021,2022' ou intervalo '2014:2024'.")
    parser.add_argument(
        "--scope",
        choices=("core", "complementary", "all"),
        default="all",
        help="Escopo do inventario: core=Sinan/Sinasc, complementary=Cnes/Sim, all=todos.",
    )
    parser.add_argument("--missing-only", action="store_true", help="Salva apenas arquivos ausentes no arquivo de saida.")
    parser.add_argument(
        "--format",
        choices=("csv", "markdown"),
        default="csv",
        help="Formato de saida do inventario.",
    )
    parser.add_argument(
        "--output",
        help="Caminho do arquivo de saida. Quando omitido, usa extensao conforme --format.",
    )
    parser.add_argument(
        "--scan-files",
        action="store_true",
        help="Inventaria arquivos reais em data/raw, data/ignored e arquivos zip preservados.",
    )
    parser.add_argument(
        "--docs-output",
        default="docs/inventario_bases.md",
        help="Caminho do Markdown resumido quando --scan-files for usado.",
    )
    return parser.parse_args()


def relative(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


DATASUS_TRANSFER_URL = "https://datasus.saude.gov.br/transferencia-de-arquivos/"


def expected_file_for(source: str, year: int) -> str:
    yy = str(year)[-2:]
    if source == "SINAN/SIFCBR":
        return f"SIFCBR{yy}.dbc"
    if source == "SINASC":
        return f"DNRS{year}.dbc"
    if source == "CNES/ST":
        return f"STRS{yy}12.dbc"
    if source == "SIM/DO":
        return f"DORS{year}.dbc"
    raise ValueError(f"Fonte desconhecida: {source}")


def target_path_for(source: str, year: int) -> Path:
    yy = str(year)[-2:]
    if source == "SINAN/SIFCBR":
        return ROOT / f"data/raw/sinan/sifilis_congenita/SIFCBR{yy}.dbc"
    if source == "SINASC":
        return ROOT / f"data/raw/sinasc/DNRS{year}.dbc"
    if source == "CNES/ST":
        return ROOT / f"data/raw/cnes/st/STRS{yy}12.dbc"
    if source == "SIM/DO":
        return ROOT / f"data/raw/sim/do/DORS{year}.dbc"
    raise ValueError(f"Fonte desconhecida: {source}")


def source_hint_for(source: str) -> str:
    hints = {
        "SINAN/SIFCBR": "DATASUS > SINAN > sifilis congenita > arquivo SIFCBR",
        "SINASC": "DATASUS > SINASC > declaracao de nascidos vivos > UF RS > arquivo DNRS",
        "CNES/ST": "DATASUS > CNES > ST > UF RS > snapshot de dezembro",
        "SIM/DO": "DATASUS > SIM > declaracao de obito > UF RS > arquivo DORS",
    }
    return hints[source]


def priority_for(source: str) -> str:
    return "obrigatorio" if source in {"SINAN/SIFCBR", "SINASC"} else "complementar"


def inventory_source(source: str, year: int, expected_kind: str, candidates: list[Path]) -> InventoryRow:
    path = first_existing(candidates)
    expected_file = expected_file_for(source, year)
    target_path = target_path_for(source, year)
    if path:
        return InventoryRow(
            source,
            year,
            expected_kind,
            priority_for(source),
            expected_file,
            "presente",
            relative(path),
            relative(target_path),
            DATASUS_TRANSFER_URL,
            source_hint_for(source),
        )
    return InventoryRow(
        source,
        year,
        expected_kind,
        priority_for(source),
        expected_file,
        "ausente",
        " ou ".join(relative(candidate) for candidate in candidates),
        relative(target_path),
        DATASUS_TRANSFER_URL,
        source_hint_for(source),
    )


def build_inventory(years: list[int], scope: str = "all") -> list[InventoryRow]:
    rows: list[InventoryRow] = []
    for year in years:
        if scope in {"core", "all"}:
            rows.append(inventory_source("SINAN/SIFCBR", year, "sifilis_congenita", default_sinan_candidates(year)))
            rows.append(inventory_source("SINASC", year, "nascidos_vivos", default_sinasc_candidates(year)))
        if scope in {"complementary", "all"}:
            rows.append(inventory_source("CNES/ST", year, "estabelecimentos_dezembro", default_cnes_st_candidates(year)))
            rows.append(inventory_source("SIM/DO", year, "obitos_gerais", default_sim_do_candidates(year)))
    return rows


def write_inventory(rows: list[InventoryRow], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as fp:
        fieldnames = list(asdict(rows[0]).keys()) if rows else list(InventoryRow.__dataclass_fields__)
        writer = csv.DictWriter(fp, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(asdict(row) for row in rows)


def write_markdown_inventory(rows: list[InventoryRow], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    missing_rows = [row for row in rows if row.status == "ausente"]
    required_missing = [row for row in missing_rows if row.priority == "obrigatorio"]
    complementary_missing = [row for row in missing_rows if row.priority == "complementar"]

    lines = [
        "# Arquivos DATASUS Necessarios",
        "",
        f"- Total de itens listados: {len(rows)}",
        f"- Arquivos ausentes: {len(missing_rows)}",
        f"- Obrigatorios ausentes: {len(required_missing)}",
        f"- Complementares ausentes: {len(complementary_missing)}",
        "",
        "Baixe os arquivos pelo portal oficial do DATASUS: https://datasus.saude.gov.br/transferencia-de-arquivos/",
        "",
    ]

    for title, group in (
        ("Obrigatorios", required_missing),
        ("Complementares", complementary_missing),
    ):
        lines.extend([f"## {title}", ""])
        if not group:
            lines.extend(["Nenhum arquivo ausente.", ""])
            continue
        lines.extend(["| Ano | Fonte | Arquivo | Colocar em | Caminho no DATASUS |", "| --- | --- | --- | --- | --- |"])
        for row in group:
            lines.append(
                f"| {row.year} | {row.source} | `{row.expected_file}` | `{row.target_path}` | {row.source_hint} |"
            )
        lines.append("")

    output.write_text("\n".join(lines), encoding="utf-8")


def default_output_for(format_name: str) -> Path:
    suffix = "md" if format_name == "markdown" else "csv"
    return ROOT / f"data/profiles/datasus_inventory.{suffix}"


def year_from_two_digits(value: str) -> int:
    return 2000 + int(value)


def status_for_path(path: Path) -> str:
    normalized = relative(path)
    if normalized.startswith("data/ignored/"):
        return "ignorado"
    if normalized.startswith("data/raw/archives/"):
        return "preservado"
    return "disponivel"


def classify_file(path: Path, archive_entry: str | None = None) -> FileInventoryRow:
    name = archive_entry or path.name
    status = "preservado" if archive_entry else status_for_path(path)
    caminho = f"{relative(path)}::{archive_entry}" if archive_entry else relative(path)
    suffix = Path(name).suffix.lower().replace(".", "").upper() or "ZIP"
    base = "Outros"
    year = ""
    uf = ""
    tipo = "nao_classificado"
    observations = ""

    upper_name = name.upper()
    if match := re.match(r"^SIFCBR(\d{2})\.DBC$", upper_name):
        base = "SINAN"
        year = str(year_from_two_digits(match.group(1)))
        uf = "BR"
        tipo = "sifilis_congenita"
    elif match := re.match(r"^DNRS(\d{4})\.DBC$", upper_name):
        base = "SINASC"
        year = match.group(1)
        uf = "RS"
        tipo = "nascidos_vivos"
    elif match := re.match(r"^DNEX(\d{4})\.DBC$", upper_name):
        base = "SINASC"
        year = match.group(1)
        uf = "EX"
        tipo = "nascidos_vivos_exterior"
        status = "fora_de_escopo"
        observations = "Arquivo DNEX nao compoe o recorte Rio Grande do Sul."
    elif match := re.match(r"^DORS(\d{4})\.DBC$", upper_name):
        base = "SIM"
        year = match.group(1)
        uf = "RS"
        tipo = "obitos_gerais"
    elif match := re.match(r"^DOFET(\d{2})\.DBC$", upper_name):
        base = "SIM"
        year = str(year_from_two_digits(match.group(1)))
        uf = "RS"
        tipo = "obitos_fetais"
    elif match := re.match(r"^DOINF(\d{2})\.DBC$", upper_name):
        base = "SIM"
        year = str(year_from_two_digits(match.group(1)))
        uf = "RS"
        tipo = "obitos_infantis"
    elif match := re.match(r"^DOMAT(\d{2})\.DBC$", upper_name):
        base = "SIM"
        year = str(year_from_two_digits(match.group(1)))
        uf = "RS"
        tipo = "obitos_maternos"
        observations = "Complementar de baixa prioridade."
    elif match := re.match(r"^(ST|EP|SR|LT|PF)([A-Z]{2})(\d{2})(\d{2})\.DBC$", upper_name):
        prefix, uf, yy, mm = match.groups()
        base = "CNES"
        year = str(year_from_two_digits(yy))
        tipo = f"{prefix.lower()}_mes_{mm}"
        if prefix == "ST" and uf == "RS" and mm == "12" and 2015 <= int(year) <= 2024:
            observations = "Snapshot principal de dezembro para estabelecimentos."
        elif prefix in {"EP", "SR"} and uf == "RS" and mm == "12" and 2015 <= int(year) <= 2024:
            observations = "Snapshot complementar de dezembro."
        else:
            status = "ignorado"
            observations = "Fora do recorte principal de CNES."
    elif match := re.match(r"^POP([ST])BR(\d{2})\.(DBF|ZIP)$", upper_name):
        base = "Populacao DATASUS"
        year = str(year_from_two_digits(match.group(2)))
        uf = "BR"
        tipo = "populacao_residente"
        observations = "Base complementar; nao substitui o denominador SINASC."
    elif match := re.match(r"^POP(\d{2})\.DBF$", upper_name):
        base = "Populacao DATASUS"
        year = str(year_from_two_digits(match.group(1)))
        uf = "BR"
        tipo = "populacao_residente"
        observations = "Base complementar; nao substitui o denominador SINASC."
    elif match := re.match(r"^POPT([A-Z]{2})(\d{2})\.DBF$", upper_name):
        base = "Populacao DATASUS"
        uf = match.group(1)
        year = str(year_from_two_digits(match.group(2)))
        tipo = "populacao_residente_uf"
        if uf != "RS":
            status = "ignorado"
            observations = "UF fora do recorte principal."
        else:
            observations = "Base complementar; nao substitui o denominador SINASC."
    elif upper_name.endswith(".ZIP"):
        tipo = "arquivo_compactado"
        observations = "Arquivo original preservado."

    return FileInventoryRow(base, name, year, uf, tipo, suffix, status, caminho, observations)


def scan_zip_entries(path: Path) -> list[FileInventoryRow]:
    rows: list[FileInventoryRow] = []
    try:
        with zipfile.ZipFile(path) as archive:
            for entry in archive.infolist():
                if entry.is_dir():
                    continue
                rows.append(classify_file(path, entry.filename))
    except zipfile.BadZipFile:
        rows.append(
            FileInventoryRow(
                "Outros",
                path.name,
                "",
                "",
                "zip_invalido",
                "ZIP",
                "erro",
                relative(path),
                "Nao foi possivel abrir o arquivo compactado.",
            )
        )
    return rows


def scan_files() -> list[FileInventoryRow]:
    roots = [ROOT / "data/raw", ROOT / "data/ignored"]
    rows: list[FileInventoryRow] = []
    seen: set[str] = set()
    for base_path in roots:
        if not base_path.exists():
            continue
        for path in sorted(item for item in base_path.rglob("*") if item.is_file()):
            if path.name == ".gitkeep":
                continue
            key = relative(path)
            if key in seen:
                continue
            seen.add(key)
            rows.append(classify_file(path))
            if path.suffix.lower() == ".zip":
                rows.extend(scan_zip_entries(path))
    return rows


def write_file_inventory(rows: list[FileInventoryRow], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as fp:
        writer = csv.DictWriter(fp, fieldnames=list(FileInventoryRow.__dataclass_fields__))
        writer.writeheader()
        writer.writerows(asdict(row) for row in rows)


def coverage_status(rows: list[FileInventoryRow], base: str, tipo: str, years: list[int]) -> list[tuple[int, str]]:
    available = {
        int(row.ano)
        for row in rows
        if row.base == base and row.tipo == tipo and row.status in {"disponivel", "preservado"} and row.ano.isdigit()
    }
    return [(year, "presente" if year in available else "faltante") for year in years]


def cnes_selected_rows(rows: list[FileInventoryRow]) -> list[FileInventoryRow]:
    return [
        row
        for row in rows
        if row.base == "CNES"
        and row.status == "disponivel"
        and row.uf == "RS"
        and row.tipo in {"st_mes_12", "ep_mes_12", "sr_mes_12"}
        and row.ano.isdigit()
        and 2015 <= int(row.ano) <= 2024
    ]


def write_docs_inventory(rows: list[FileInventoryRow], output: Path, years: list[int]) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Inventario Das Bases",
        "",
        "Inventario gerado a partir dos arquivos organizados em `data/raw/` e `data/ignored/`.",
        "",
        "## Cobertura Principal",
        "",
        "| Base | Tipo | Ano | Status |",
        "| --- | --- | --- | --- |",
    ]
    for base, tipo in (
        ("SINAN", "sifilis_congenita"),
        ("SINASC", "nascidos_vivos"),
        ("SIM", "obitos_gerais"),
    ):
        for year, status in coverage_status(rows, base, tipo, years):
            lines.append(f"| {base} | {tipo} | {year} | {status} |")

    lines.extend(
        [
            "",
            "## CNES Selecionado",
            "",
            "O CNES e mensal. Para evitar duplicidade cadastral, o recorte principal usa dezembro de cada ano.",
            "",
            "| Base | Arquivo | Ano | UF | Tipo | Status | Observacoes |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in sorted(cnes_selected_rows(rows), key=lambda item: (item.tipo, item.ano, item.arquivo)):
        lines.append(
            f"| {row.base} | `{row.arquivo}` | {row.ano} | {row.uf} | {row.tipo} | {row.status} | {row.observacoes} |"
        )

    lines.extend(
        [
            "",
            "## Resumo Por Status",
            "",
            "| Base | Status | Quantidade |",
            "| --- | --- | --- |",
        ]
    )
    counts: dict[tuple[str, str], int] = {}
    for row in rows:
        key = (row.base, row.status)
        counts[key] = counts.get(key, 0) + 1
    for (base, status), count in sorted(counts.items()):
        lines.append(f"| {base} | {status} | {count} |")

    lines.extend(
        [
            "",
            "## Observacoes",
            "",
            "- SINASC segue como denominador principal da incidencia de sifilis congenita.",
            "- Populacao DATASUS e complementar e nao substitui nascidos vivos do SINASC.",
            "- SIM e complementar e nao compoe o indicador principal de incidencia.",
            "- Arquivos ignorados foram preservados em `data/ignored/` para auditoria.",
            "- O inventario detalhado em CSV fica em `data/profiles/datasus_file_inventory.csv`.",
            "",
        ]
    )
    output.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    years = parse_years(args.year, args.years)
    if args.scan_files:
        rows = scan_files()
        output = resolve_project_path(args.output) if args.output else ROOT / "data/profiles/datasus_file_inventory.csv"
        write_file_inventory(rows, output)
        docs_output = resolve_project_path(args.docs_output)
        write_docs_inventory(rows, docs_output, years)
        print(f"Inventario detalhado salvo em: {relative(output)}")
        print(f"Inventario Markdown salvo em: {relative(docs_output)}")
        print(f"Arquivos inventariados: {len(rows)}")
        return

    rows = build_inventory(years, scope=args.scope)
    if args.missing_only:
        rows = [row for row in rows if row.status == "ausente"]
    output = resolve_project_path(args.output) if args.output else default_output_for(args.format)
    if args.format == "csv":
        write_inventory(rows, output)
    else:
        write_markdown_inventory(rows, output)

    present = sum(1 for row in rows if row.status == "presente")
    missing = len(rows) - present
    print(f"Inventario salvo em: {relative(output)}")
    print(f"Arquivos presentes: {present}")
    print(f"Arquivos ausentes: {missing}")


if __name__ == "__main__":
    main()
