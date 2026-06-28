# Sífilis Congênita em Porto Alegre

Projeto de dados para análise de sífilis congênita em Porto Alegre, com foco em desigualdades raciais, acesso ao pré-natal e perfil materno. O repositório combina microdados públicos do DATASUS, pipeline ETL em Python, PostgreSQL, consultas SQL e notebooks analíticos.

Documentação completa:

- [Português](docs/README.pt-BR.md)
- [English](docs/README.en.md)

## Execução Rápida

```bash
docker compose up -d
python -m pip install -r requirements.txt
python -m src.etl.load_datasus --strict
```

## English

Data project for congenital syphilis analysis in Porto Alegre, focused on racial inequalities, prenatal care access, and maternal profile. The repository combines public DATASUS microdata, a Python ETL pipeline, PostgreSQL, SQL queries, and analytical notebooks.

Full documentation:

- [Português](docs/README.pt-BR.md)
- [English](docs/README.en.md)

## Quick Start

```bash
docker compose up -d
python -m pip install -r requirements.txt
python -m src.etl.load_datasus --strict
```
