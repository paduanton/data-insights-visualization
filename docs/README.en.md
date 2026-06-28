# Congenital Syphilis In Porto Alegre

## Overview

This project organizes an analytical pipeline to study congenital syphilis in Porto Alegre using public microdata. It focuses on the relationship between maternal race/color, prenatal care access, maternal education, and incidence of reported cases.

The repository combines:

- extraction and loading of DATASUS `.dbc` microdata;
- a PostgreSQL database with `bronze`, `silver`, and `gold` layers;
- SQL queries for validation and indicators;
- notebooks for analysis and visualization;
- documentation of produced results.

## Data Sources

Core sources:

- `data/raw/SIFCBR24.dbc`: SINAN/SIFCBR 2024, congenital syphilis notifications.
- `data/raw/sinasc/DNRS2024.dbc`: SINASC 2024, live births in Rio Grande do Sul.

Sources preserved for expansion:

- `data/raw/cnes/STRS2401.dbc` to `data/raw/cnes/STRS2412.dbc`: CNES 2024.
- `data/raw/sim/DORS2024.dbc`: SIM 2024, general deaths.
- `data/raw/sim/DOFET24.dbc`: SIM 2024, fetal deaths.
- `data/raw/sim/DOMAT24.dbc`: SIM 2024, maternal deaths.

Original archives preserved:

- `data/raw/archives/sinasc_rs_2024_dn.zip`
- `data/raw/archives/cnes_rs_2024_st_mensal.zip`
- `data/raw/archives/sim_rs_2024_obitos_gerais.zip`
- `data/raw/archives/sim_rs_2024_obitos_fetais_maternos.zip`

Conceptual reference preserved:

- `docs/references/anteprojeto_sifilis_congenita_poars.pdf`

## Architecture

The pipeline uses PostgreSQL as a local analytical database.

- `bronze`: raw tables loaded from `.dbc` files.
- `silver`: views with normalized codes and categories.
- `gold`: aggregated views for indicators and analytical queries.

Image to add:

- `docs/assets/architecture.png`

## Local Execution

Start PostgreSQL:

```bash
docker compose up -d
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Run the load:

```bash
python -m src.etl.load_datasus --strict
```

The `--strict` mode validates the expected counts for the 2024 files included in the repository.

## ETL Pipeline

The ETL converts `.dbc` files to `.dbf`, reads records with `dbfread`, normalizes column names, and loads the data into PostgreSQL. The load is idempotent by year: when the same year is loaded again, previous records for that year are replaced.

Image to add:

- `docs/assets/etl-flow.png`

## Queries

Initial queries:

- `database/queries/01_validacao_carga.sql`: raw counts and Porto Alegre subset.
- `database/queries/02_indicadores_municipio.sql`: incidence per 1,000 live births.
- `database/queries/03_desigualdades_prenatal_escolaridade.sql`: education among cases without prenatal care by racial group.
- `database/queries/04_qualidade_registros.sql`: percentage of ignored records by critical variable.

Each new query must answer an explicit analytical question and, when it produces a relevant result, it must be documented in this file and in `docs/README.pt-BR.md`.

## Notebooks

Notebooks should live in `notebooks/analytics/` and answer specific analytical questions. The existing visualization notebook remains as an initial project reference.

## Results

Existing visualization:

- `outputs/images/graficos/visualizacao_sifilis_congenita_poars_escolaridade_sem_prenatal.png`

Images for new results should be added under:

- `docs/assets/results/`

## Limitations

- Public datasets will not be used for individual-level linkage between SINAN and SINASC.
- The main analytical unit is aggregated by municipality, year, and strata.
- Ignored or missing categories are preserved and measured.
- CNES, SIM, IBGE, and other sources are complementary layers, not dependencies for the first load.
