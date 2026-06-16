# Inventario de dados

Este repositorio organiza os microdados brutos em `data/raw/`, mantendo os arquivos ZIP originais em `data/raw/archives/`.

## Bases principais para a visualizacao

- `data/raw/SIFCBR24.dbc`: SINAN/SIFCBR 2024, notificacoes de sifilis congenita.
- `data/raw/sinasc/DNRS2024.dbc`: SINASC 2024, nascidos vivos no Rio Grande do Sul.
- `data/raw/cnes/STRS2401.dbc` a `data/raw/cnes/STRS2412.dbc`: CNES 2024, arquivos mensais de estabelecimentos do Rio Grande do Sul.

## Bases complementares

- `data/raw/sim/DORS2024.dbc`: SIM 2024, obitos do Rio Grande do Sul.
- `data/raw/sim/DOFET24.dbc`: SIM 2024, obitos fetais.
- `data/raw/sim/DOMAT24.dbc`: SIM 2024, obitos maternos.

Arquivos de origem preservados:

- `data/raw/archives/SIM.zip`: contem `DORS2024.dbc`.
- `data/raw/archives/SIM2.zip`: contem `DOFET24.dbc`, `DOMAT24.dbc` e uma copia de `DORS2024.dbc`.

## Referencia do anteprojeto

- `docs/references/anteprojeto_sifilis_congenita_poars.pdf`: copia local do anteprojeto.
- `docs/references/anteprojeto_sifilis_congenita_poars.txt`: texto extraido para consulta rapida.

## Recorte inicial

A visualizacao inicial usa Porto Alegre como municipio de residencia (`431490`) e cruza:

- SINASC como contexto dos nascidos vivos;
- SINAN/SIFCBR como casos de sifilis congenita;
- raca/cor materna como eixo central de desigualdade;
- pre-natal como indicador auxiliar de acesso ao cuidado.
