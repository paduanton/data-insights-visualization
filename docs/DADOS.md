# Inventário de dados

Este repositório organiza os microdados brutos em `data/raw/`, mantendo os arquivos ZIP originais em `data/raw/archives/`.

## Bases principais para a visualização

- `data/raw/SIFCBR24.dbc`: SINAN/SIFCBR 2024, notificações de sífilis congênita.
- `data/raw/sinasc/DNRS2024.dbc`: SINASC 2024, nascidos vivos no Rio Grande do Sul.
- `data/raw/cnes/STRS2401.dbc` a `data/raw/cnes/STRS2412.dbc`: CNES 2024, arquivos mensais de estabelecimentos do Rio Grande do Sul.

## Bases complementares

- `data/raw/sim/DORS2024.dbc`: SIM 2024, óbitos do Rio Grande do Sul.
- `data/raw/sim/DOFET24.dbc`: SIM 2024, óbitos fetais.
- `data/raw/sim/DOMAT24.dbc`: SIM 2024, óbitos maternos.

Arquivos de origem preservados:

- `data/raw/archives/SIM.zip`: contém `DORS2024.dbc`.
- `data/raw/archives/SIM2.zip`: contém `DOFET24.dbc`, `DOMAT24.dbc` e uma cópia de `DORS2024.dbc`.

## Referência do anteprojeto

- `docs/references/anteprojeto_sifilis_congenita_poars.pdf`: cópia local do anteprojeto.
- `docs/references/anteprojeto_sifilis_congenita_poars.txt`: texto extraído para consulta rápida.

## Recorte inicial

A visualização inicial usa Porto Alegre como município de residência (`431490`) e cruza:

- SINASC como contexto dos nascidos vivos;
- SINAN/SIFCBR como casos de sífilis congênita;
- raça/cor materna como eixo central de desigualdade;
- pré-natal como indicador auxiliar de acesso ao cuidado.
