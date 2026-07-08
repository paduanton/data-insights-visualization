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

- `data/raw/sinan/sifilis_congenita/SIFCBR15.dbc` to `data/raw/sinan/sifilis_congenita/SIFCBR24.dbc`: SINAN/SIFCBR 2015-2024, congenital syphilis notifications.
- `data/raw/sinasc/DNRS2015.dbc` to `data/raw/sinasc/DNRS2024.dbc`: SINASC 2015-2024, live births in Rio Grande do Sul.

Sources preserved for expansion:

- `data/raw/cnes/st/STRS1512.dbc` to `data/raw/cnes/st/STRS2412.dbc`: CNES/ST, December of each year as the annual snapshot.
- `data/raw/cnes/ep/` and `data/raw/cnes/sr/`: complementary CNES, also filtered to December 2015-2024.
- `data/raw/sim/do/DORS2015.dbc` to `data/raw/sim/do/DORS2024.dbc`: SIM 2015-2024, general deaths.
- `data/raw/sim/dofet/`, `data/raw/sim/doinf/`, and `data/raw/sim/domat/`: complementary SIM.
- `data/raw/populacao_datasus/`: complementary DATASUS/IBGE population.

Auxiliary source for inventory and validation:

- Base dos Dados through `basedosdados` and `google-cloud-bigquery`, with auditing of useful BigQuery tables for SINASC, SIM, CNES, municipal population, SIH, and SINAN technical reference.

Structure for historical consolidation:

- `data/raw/sinan/sifilis_congenita/`: `SIFCBR*.dbc` files.
- `data/raw/sinasc/`: `DNRS*.dbc` files.
- `data/raw/cnes/st/`: CNES `STRS*.dbc` files.
- `data/raw/cnes/ep/` and `data/raw/cnes/sr/`: complementary December CNES files.
- `data/raw/sim/do/`: SIM `DORS*.dbc` files.
- `data/raw/populacao_datasus/`: complementary population files.
- `data/ignored/`: preserved files outside the main scope.
- `data/staging/`: exploratory conversions.
- `data/profiles/`: profiles generated before the final schema.

Consolidated inventory for the `2015-2024` window:

- `docs/inventario_bases.md`: main coverage, selected CNES files, and summary of preserved/ignored files.
- `data/profiles/datasus_file_inventory.csv`: detailed inventory generated locally.

To check missing files in the current cut:

```bash
python -m src.etl.inventory_datasus --years 2015:2024 --missing-only --output data/profiles/datasus_missing_files_2015_2024.csv
```

To regenerate the detailed inventory:

```bash
python -m src.etl.inventory_datasus --years 2015:2024 --scan-files --output data/profiles/datasus_file_inventory.csv --docs-output docs/inventario_bases.md
```

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

PgAdmin is available at `http://localhost:5050`. Use `PGADMIN_DEFAULT_EMAIL` and `PGADMIN_DEFAULT_PASSWORD` from `.env`; the defaults in `.env.example` are `admin@example.com` and `admin`.

To register the database in PgAdmin, use:

- host: `postgres`
- port: `5432`
- database: `sifilis_analytics`
- user: `postgres`
- password: `postgres`

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Run the load:

```bash
python -m src.etl.load_datasus --strict
```

The `--strict` mode validates the expected counts for the 2024 files included in the repository.

For multi-year loads, use:

```bash
python -m src.etl.load_datasus --years 2015:2024
```

The multi-year command searches the planned historical structure and also preserves fallback paths for the current 2024 MVP.

Before downloading new files, generate an inventory:

```bash
python -m src.etl.inventory_datasus --years 2015:2024
```

For a manual download list, use:

```bash
python -m src.etl.inventory_datasus --years 2015:2024 --missing-only --format markdown --output data/profiles/datasus_missing_files_2015_2024.md
```

For complementary sources validated through profiling, separate bronze loaders are available:

```bash
python -m src.etl.load_cnes --years 2015:2024 --month 12
python -m src.etl.load_sim --years 2015:2024
```

## ETL Pipeline

The ETL converts `.dbc` files to `.dbf`, reads records with `dbfread`, normalizes column names, and loads the data into PostgreSQL. The load is idempotent by year: when the same year is loaded again, previous records for that year are replaced. In `bronze` tables, new columns found in later years are added as `TEXT`, preserving microdata variations until the final schema decision.

Image to add:

- `docs/assets/etl-flow.png`

Before the final analytical schema, generate exploratory profiles:

```bash
python -m src.etl.profile_datasus --years 2015:2024
```

To include complementary sources in profiling:

```bash
python -m src.etl.profile_datasus --years 2015:2024 --skip-core --include-cnes --output data/profiles/cnes_st_column_profile_2015_2024.csv
python -m src.etl.profile_datasus --years 2015:2024 --skip-core --include-sim --output data/profiles/sim_do_column_profile_2015_2024.csv
```

Profiles are saved under `data/profiles/` and should guide final column, category, and view decisions.

## Queries

Initial queries:

- `database/queries/01_validacao_carga.sql`: raw counts and Porto Alegre subset.
- `database/queries/02_indicadores_municipio.sql`: incidence per 1,000 live births.
- `database/queries/03_desigualdades_prenatal_escolaridade.sql`: education among cases without prenatal care by racial group.
- `database/queries/04_qualidade_registros.sql`: percentage of ignored records by critical variable.
- `database/queries/05_incidencia_por_grupo_racial.sql`: estimated incidence by maternal racial group.
- `database/queries/06_prenatal_por_grupo_racial.sql`: prenatal care status by maternal racial group.
- `database/queries/07_diagnostico_materno_por_grupo_racial.sql`: maternal diagnosis timing by racial group.
- `database/queries/08_razao_incidencia_grupo_racial.sql`: incidence ratio between Black and non-Black mothers.
- `database/queries/09_inventario_campos_cuidado_materno.sql`: inspection of candidate fields for prenatal care, diagnosis, treatment, education, age, and race/color.

Each new query must answer an explicit analytical question and, when it produces a relevant result, it must be documented in this file and in `docs/README.pt-BR.md`.

## Notebooks

Notebooks should live in `notebooks/analytics/` and answer specific analytical questions. The existing visualization notebook remains as an initial project reference.

Initial notebooks:

- `notebooks/analytics/00_validacao_ambiente_dados.ipynb`: environment, Docker, tests, and strict load validation.
- `notebooks/analytics/01_overview_sifilis_congenita.ipynb`: Porto Alegre subset overview and general incidence.
- `notebooks/analytics/02_auditoria_basedosdados.ipynb`: coverage, cost, and possible-use audit for Base dos Dados.
- `notebooks/analytics/03_prenatal_raca_escolaridade.ipynb`: prenatal care, race/color, and education cross-analysis.
- `notebooks/analytics/04_perfil_colunas_qualidade.ipynb`: column and critical-variable profiling before the final schema.
- `notebooks/analytics/05_serie_historica_incidencia.ipynb`: annual incidence trend in Porto Alegre.
- `notebooks/analytics/06_desigualdade_racial_incidencia.ipynb`: incidence and incidence ratio by racial group.
- `notebooks/analytics/07_diagnostico_tratamento_cuidado.ipynb`: maternal diagnosis and basis for treatment analysis.
- `notebooks/analytics/08_contexto_cnes_ibge_sim.ipynb`: inventory and contextual use of CNES, IBGE, and SIM.

## Notebook Reference

Each notebook should be run from the repository root or through Google Colab. When using Colab, load the repository data and keep the paths defined inside the notebook.

| Notebook | Main question | Google Colab | Result image |
| --- | --- | --- | --- |
| `notebooks/visualizacao_sifilis_congenita_poars.ipynb` | Among congenital syphilis cases without prenatal care in Porto Alegre, how is maternal education distributed by racial group? | [Open in Colab](https://colab.research.google.com/github/paduanton/data-insights-visualization/blob/main/notebooks/visualizacao_sifilis_congenita_poars.ipynb) | `outputs/images/graphs/visualizacao_sifilis_congenita_poars_escolaridade_sem_prenatal.png` |
| `notebooks/analytics/00_validacao_ambiente_dados.ipynb` | Can the environment reproduce the 2024 MVP before historical expansion? | [Open in Colab](https://colab.research.google.com/github/paduanton/data-insights-visualization/blob/main/notebooks/analytics/00_validacao_ambiente_dados.ipynb) | `docs/assets/results/validacao_ambiente_dados.png` |
| `notebooks/analytics/01_overview_sifilis_congenita.ipynb` | What is the overview of reported cases, live births, and general incidence in Porto Alegre? | [Open in Colab](https://colab.research.google.com/github/paduanton/data-insights-visualization/blob/main/notebooks/analytics/01_overview_sifilis_congenita.ipynb) | `docs/assets/results/overview_sifilis_congenita.png` |
| `notebooks/analytics/02_auditoria_basedosdados.ipynb` | Which Base dos Dados tables can complement or validate the project's DATASUS sources? | [Open in Colab](https://colab.research.google.com/github/paduanton/data-insights-visualization/blob/main/notebooks/analytics/02_auditoria_basedosdados.ipynb) | `docs/assets/results/auditoria_basedosdados_periodos.png` |
| `notebooks/analytics/03_prenatal_raca_escolaridade.ipynb` | How do prenatal care, race/color, and education combine across reported cases? | [Open in Colab](https://colab.research.google.com/github/paduanton/data-insights-visualization/blob/main/notebooks/analytics/03_prenatal_raca_escolaridade.ipynb) | `docs/assets/results/prenatal_raca_escolaridade.png` |
| `notebooks/analytics/04_perfil_colunas_qualidade.ipynb` | Which columns and critical variables support the final analytical schema? | [Open in Colab](https://colab.research.google.com/github/paduanton/data-insights-visualization/blob/main/notebooks/analytics/04_perfil_colunas_qualidade.ipynb) | `docs/assets/results/perfil_colunas_qualidade.png` |
| `notebooks/analytics/05_serie_historica_incidencia.ipynb` | How does congenital syphilis incidence evolve across loaded years? | [Open in Colab](https://colab.research.google.com/github/paduanton/data-insights-visualization/blob/main/notebooks/analytics/05_serie_historica_incidencia.ipynb) | `docs/assets/results/serie_historica_incidencia.png` |
| `notebooks/analytics/06_desigualdade_racial_incidencia.ipynb` | Does estimated incidence differ between Black and non-Black mothers? | [Open in Colab](https://colab.research.google.com/github/paduanton/data-insights-visualization/blob/main/notebooks/analytics/06_desigualdade_racial_incidencia.ipynb) | `docs/assets/results/desigualdade_racial_incidencia.png` |
| `notebooks/analytics/07_diagnostico_tratamento_cuidado.ipynb` | Does maternal diagnosis timing indicate differences in recorded care? | [Open in Colab](https://colab.research.google.com/github/paduanton/data-insights-visualization/blob/main/notebooks/analytics/07_diagnostico_tratamento_cuidado.ipynb) | `docs/assets/results/diagnostico_materno_grupo_racial.png` |
| `notebooks/analytics/08_contexto_cnes_ibge_sim.ipynb` | Which complementary sources can contextualize service supply, population, and outcomes? | [Open in Colab](https://colab.research.google.com/github/paduanton/data-insights-visualization/blob/main/notebooks/analytics/08_contexto_cnes_ibge_sim.ipynb) | `docs/assets/results/contexto_cnes_ibge_sim.png` |

When creating a new notebook, add a new row to this table and apply the same update to `docs/README.pt-BR.md`. The result image should be saved under `docs/assets/results/` when it is part of the project documentation, or under `outputs/images/` when it is an operational notebook output.

## Results

Existing visualization:

- `outputs/images/graphs/visualizacao_sifilis_congenita_poars_escolaridade_sem_prenatal.png`

Initial validated results for 2024:

- SINAN/SIFCBR: `12762` records in Rio Grande do Sul.
- SINASC: `111988` records in Rio Grande do Sul.
- Porto Alegre: `137` congenital syphilis cases and `12850` live births.
- Estimated general incidence: `10.66` cases per 1,000 live births.
- Cases without prenatal care: `10` among Black mothers and `14` among non-Black mothers.

Images for new results should be added under:

- `docs/assets/results/`

Recommended image for the next result:

- `docs/assets/results/incidencia_por_grupo_racial.png`
- `docs/assets/results/razao_incidencia_grupo_racial.png`
- `docs/assets/results/auditoria_basedosdados_periodos.png`
- `docs/assets/results/perfil_colunas_qualidade.png`
- `docs/assets/results/serie_historica_incidencia.png`
- `docs/assets/results/desigualdade_racial_incidencia.png`
- `docs/assets/results/diagnostico_materno_grupo_racial.png`

## Limitations

- Public datasets will not be used for individual-level linkage between SINAN and SINASC.
- The main analytical unit is aggregated by municipality, year, and strata.
- Ignored or missing categories are preserved and measured.
- CNES, SIM, IBGE, and other sources are complementary layers, not dependencies for the first load.
