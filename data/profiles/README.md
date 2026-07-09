# Data Profiles

This directory keeps lightweight generated evidence used to audit source coverage, schema stability, and data quality.

Tracked files are aggregate metadata only. They do not contain individual DATASUS records.

Tracked evidence:

- `basedosdados_audit.csv`: BigQuery audit summary for candidate Base dos Dados tables.
- `basedosdados_year_series.csv`: annual record counts from the audited Base dos Dados tables.
- `datasus_file_inventory.csv`: source-file inventory used to validate extraction and organization.
- `datasus_missing_files_2015_2024.csv` and `datasus_missing_files_2015_2024.md`: expected-file coverage for the current 2015-2024 scope.
- `datasus_column_profile_2015_2024.csv`: column-level profile for core SINAN/SIFCBR and SINASC sources.
- `cnes_st_column_profile_2015_2024.csv`: column-level profile for CNES/ST December snapshots.
- `sim_do_column_profile_2015_2024.csv`: column-level profile for SIM/DO complementary records.

Ignored files in this directory are local rebuild artifacts, obsolete profile runs, or generated images that already exist in `docs/assets/results/`.
