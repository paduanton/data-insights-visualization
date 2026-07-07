from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from src.config import ROOT, resolve_project_path


@dataclass(frozen=True)
class DatasusSourcePair:
    year: int
    sinan: Path
    sinasc: Path


def parse_years(year: int | None, years: str | None) -> list[int]:
    if years:
        value = years.strip()
        if ":" in value:
            start_text, end_text = value.split(":", maxsplit=1)
            start = int(start_text)
            end = int(end_text)
            if end < start:
                raise ValueError("--years deve usar intervalo crescente, por exemplo 2014:2024.")
            return list(range(start, end + 1))
        return sorted({int(item.strip()) for item in value.split(",") if item.strip()})
    if year is None:
        return [2024]
    return [year]


def format_template(template: str, year: int) -> Path:
    return resolve_project_path(template.format(year=year, yy=str(year)[-2:]))


def default_sinan_candidates(year: int) -> list[Path]:
    yy = str(year)[-2:]
    return [
        ROOT / f"data/raw/sinan/sifilis_congenita/SIFCBR{yy}.dbc",
        ROOT / f"data/raw/SIFCBR{yy}.dbc",
    ]


def default_sinasc_candidates(year: int) -> list[Path]:
    return [
        ROOT / f"data/raw/sinasc/DNRS{year}.dbc",
        ROOT / f"data/raw/sinasc/DNRS{str(year)[-2:]}.dbc",
    ]


def first_existing(candidates: list[Path]) -> Path | None:
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def resolve_datasus_sources(
    years: list[int],
    sinan: str | None = None,
    sinasc: str | None = None,
    sinan_template: str | None = None,
    sinasc_template: str | None = None,
) -> tuple[list[DatasusSourcePair], list[str]]:
    pairs: list[DatasusSourcePair] = []
    missing: list[str] = []

    for current_year in years:
        sinan_path = (
            resolve_project_path(sinan)
            if sinan and len(years) == 1
            else format_template(sinan_template, current_year)
            if sinan_template
            else first_existing(default_sinan_candidates(current_year))
        )
        sinasc_path = (
            resolve_project_path(sinasc)
            if sinasc and len(years) == 1
            else format_template(sinasc_template, current_year)
            if sinasc_template
            else first_existing(default_sinasc_candidates(current_year))
        )

        if sinan_path is None or not sinan_path.exists():
            expected = (
                sinan_template.format(year=current_year, yy=str(current_year)[-2:])
                if sinan_template
                else " ou ".join(str(path.relative_to(ROOT)) for path in default_sinan_candidates(current_year))
            )
            missing.append(f"SINAN/SIFCBR {current_year}: {expected}")

        if sinasc_path is None or not sinasc_path.exists():
            expected = (
                sinasc_template.format(year=current_year, yy=str(current_year)[-2:])
                if sinasc_template
                else " ou ".join(str(path.relative_to(ROOT)) for path in default_sinasc_candidates(current_year))
            )
            missing.append(f"SINASC {current_year}: {expected}")

        if sinan_path is not None and sinasc_path is not None and sinan_path.exists() and sinasc_path.exists():
            pairs.append(DatasusSourcePair(current_year, sinan_path, sinasc_path))

    return pairs, missing
