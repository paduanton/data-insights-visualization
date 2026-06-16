# Inventário de dados

Este repositório organiza os microdados brutos em `data/raw/`, mantendo os arquivos ZIP originais em `data/raw/archives/`.

## Base usada na visualização final

- `data/raw/SIFCBR24.dbc`: SINAN/SIFCBR 2024, notificações de sífilis congênita.

## Bases de contexto preservadas

- `data/raw/sinasc/DNRS2024.dbc`: SINASC 2024, nascidos vivos no Rio Grande do Sul.
- `data/raw/cnes/STRS2401.dbc` a `data/raw/cnes/STRS2412.dbc`: CNES 2024, arquivos mensais de estabelecimentos do Rio Grande do Sul.
- `data/raw/sim/DORS2024.dbc`: SIM 2024, óbitos do Rio Grande do Sul.
- `data/raw/sim/DOFET24.dbc`: SIM 2024, óbitos fetais.
- `data/raw/sim/DOMAT24.dbc`: SIM 2024, óbitos maternos.

Arquivos de origem preservados:

- `data/raw/archives/sinasc_rs_2024_dn.zip`: contém `DNRS2024.dbc`.
- `data/raw/archives/cnes_rs_2024_st_mensal.zip`: contém `STRS2401.dbc` a `STRS2412.dbc`.
- `data/raw/archives/sim_rs_2024_obitos_gerais.zip`: contém `DORS2024.dbc`.
- `data/raw/archives/sim_rs_2024_obitos_fetais_maternos.zip`: contém `DOFET24.dbc`, `DOMAT24.dbc` e uma cópia de `DORS2024.dbc`.

## Referência do anteprojeto

- `docs/references/anteprojeto_sifilis_congenita_poars.pdf`: cópia local do anteprojeto.

## Recorte da visualização

A visualização usa Porto Alegre como município de residência (`431490`) e cruza, nos casos notificados de sífilis congênita:

- raça/cor materna;
- realização de pré-natal;
- escolaridade materna.
