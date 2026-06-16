# Implementação prática do anteprojeto

Este módulo cria um banco analítico local em PostgreSQL para apoiar o estudo sobre desigualdade racial na sífilis congênita em Porto Alegre.

## Escopo do MVP

- Fonte primária: microdados DATASUS em `.dbc` já presentes no repositório.
- Bases carregadas nesta etapa:
  - `data/raw/SIFCBR24.dbc`: SINAN/SIFCBR 2024.
  - `data/raw/sinasc/DNRS2024.dbc`: SINASC 2024.
- Unidade analítica: município, ano e estratos agregados.
- Não há pareamento individual entre SINAN e SINASC.

## Estrutura

- `docker-compose.yml`: serviço PostgreSQL.
- `database/init/`: schemas e views analíticas.
- `database/queries/`: consultas de validação e indicadores.
- `src/etl/load_datasus.py`: carga idempotente dos arquivos `.dbc`.

## Execução

Crie um `.env` a partir de `.env.example` ou use os valores padrão.

```bash
docker compose up -d
```

Instale as dependências Python em um ambiente virtual:

```bash
python -m pip install -r requirements.txt
```

Execute a carga:

```bash
python -m src.etl.load_datasus --strict
```

O parâmetro `--strict` valida as contagens esperadas para os arquivos 2024 incluídos no repositório.

## Consultas iniciais

Após a carga, execute as consultas em `database/queries/` no PostgreSQL:

- `01_validacao_carga.sql`: contagens brutas e recorte Porto Alegre.
- `02_indicadores_municipio.sql`: incidência por 1.000 nascidos vivos.
- `03_desigualdades_prenatal_escolaridade.sql`: escolaridade nos casos sem pré-natal por grupo racial.
- `04_qualidade_registros.sql`: percentual de registros ignorados por variável crítica.

## Expansão prevista

- Adicionar anos anteriores de SINAN/SIFCBR e SINASC mantendo a parametrização por `--year`.
- Usar TabNet/DATASUS como validação histórica agregada.
- Incorporar IBGE Localidades como dimensão territorial.
- Avaliar IBGE SIDRA, Base dos Dados, CNES e SIM somente depois da carga central estar validada.
