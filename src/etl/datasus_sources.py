from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from src.config import ROOT, resolve_project_path


@dataclass(frozen=True)
class DatasusSourcePair:
    year: int
    sinan: Path
    sinasc: Path


@dataclass(frozen=True)
class DatasusSingleSource:
    year: int
    path: Path
    source: str


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


def relative_path(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


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


def default_cnes_st_candidates(year: int, month: int = 12) -> list[Path]:
    yy = str(year)[-2:]
    mm = f"{month:02d}"
    return [
        ROOT / f"data/raw/cnes/st/STRS{yy}{mm}.dbc",
        ROOT / f"data/raw/cnes/STRS{yy}{mm}.dbc",
    ]


def default_sim_do_candidates(year: int) -> list[Path]:
    return [
        ROOT / f"data/raw/sim/do/DORS{year}.dbc",
        ROOT / f"data/raw/sim/do/DORS{str(year)[-2:]}.dbc",
        ROOT / f"data/raw/sim/DORS{year}.dbc",
        ROOT / f"data/raw/sim/DORS{str(year)[-2:]}.dbc",
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
                else " ou ".join(relative_path(path) for path in default_sinan_candidates(current_year))
            )
            missing.append(f"SINAN/SIFCBR {current_year}: {expected}")

        if sinasc_path is None or not sinasc_path.exists():
            expected = (
                sinasc_template.format(year=current_year, yy=str(current_year)[-2:])
                if sinasc_template
                else " ou ".join(relative_path(path) for path in default_sinasc_candidates(current_year))
            )
            missing.append(f"SINASC {current_year}: {expected}")

        if sinan_path is not None and sinasc_path is not None and sinan_path.exists() and sinasc_path.exists():
            pairs.append(DatasusSourcePair(current_year, sinan_path, sinasc_path))

    return pairs, missing


def resolve_cnes_sources(
    years: list[int],
    month: int = 12,
    template: str | None = None,
) -> tuple[list[DatasusSingleSource], list[str]]:
    sources: list[DatasusSingleSource] = []
    missing: list[str] = []

    for current_year in years:
        path = format_template(template, current_year) if template else first_existing(default_cnes_st_candidates(current_year, month))
        if path is None or not path.exists():
            expected = (
                template.format(year=current_year, yy=str(current_year)[-2:])
                if template
                else " ou ".join(relative_path(candidate) for candidate in default_cnes_st_candidates(current_year, month))
            )
            missing.append(f"CNES ST {current_year}/{month:02d}: {expected}")
        else:
            sources.append(DatasusSingleSource(current_year, path, "CNES/ST"))

    return sources, missing


def resolve_sim_sources(
    years: list[int],
    template: str | None = None,
) -> tuple[list[DatasusSingleSource], list[str]]:
    sources: list[DatasusSingleSource] = []
    missing: list[str] = []

    for current_year in years:
        path = format_template(template, current_year) if template else first_existing(default_sim_do_candidates(current_year))
        if path is None or not path.exists():
            expected = (
                template.format(year=current_year, yy=str(current_year)[-2:])
                if template
                else " ou ".join(relative_path(candidate) for candidate in default_sim_do_candidates(current_year))
            )
            missing.append(f"SIM DO {current_year}: {expected}")
        else:
            sources.append(DatasusSingleSource(current_year, path, "SIM/DO"))

    return sources, missing
