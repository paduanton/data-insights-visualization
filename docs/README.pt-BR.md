# Sífilis Congênita em Porto Alegre

## Visão Geral

Este projeto organiza um pipeline analítico para estudar sífilis congênita em Porto Alegre a partir de microdados públicos. O foco está na relação entre raça/cor materna, acesso ao pré-natal, escolaridade materna e incidência de casos notificados.

O repositório combina:

- extração e carga de microdados DATASUS em formato `.dbc`;
- banco PostgreSQL com camadas `bronze`, `silver` e `gold`;
- consultas SQL para validação e indicadores;
- notebooks para análises e visualizações;
- documentação dos resultados produzidos.

## Fontes De Dados

Fontes centrais:

- `data/raw/SIFCBR24.dbc`: SINAN/SIFCBR 2024, notificações de sífilis congênita.
- `data/raw/sinasc/DNRS2024.dbc`: SINASC 2024, nascidos vivos no Rio Grande do Sul.

Fontes preservadas para expansão:

- `data/raw/cnes/STRS2401.dbc` a `data/raw/cnes/STRS2412.dbc`: CNES 2024.
- `data/raw/sim/DORS2024.dbc`: SIM 2024, óbitos gerais.
- `data/raw/sim/DOFET24.dbc`: SIM 2024, óbitos fetais.
- `data/raw/sim/DOMAT24.dbc`: SIM 2024, óbitos maternos.

Arquivos originais preservados:

- `data/raw/archives/sinasc_rs_2024_dn.zip`
- `data/raw/archives/cnes_rs_2024_st_mensal.zip`
- `data/raw/archives/sim_rs_2024_obitos_gerais.zip`
- `data/raw/archives/sim_rs_2024_obitos_fetais_maternos.zip`

Referência conceitual preservada:

- `docs/references/anteprojeto_sifilis_congenita_poars.pdf`

## Arquitetura

O pipeline usa PostgreSQL como banco analítico local.

- `bronze`: tabelas brutas carregadas a partir dos arquivos `.dbc`.
- `silver`: views com códigos e categorias normalizadas.
- `gold`: views agregadas para indicadores e consultas analíticas.

Imagem a adicionar:

- `docs/assets/architecture.png`

## Execução Local

Suba o PostgreSQL:

```bash
docker compose up -d
```

Instale as dependências:

```bash
python -m pip install -r requirements.txt
```

Execute a carga:

```bash
python -m src.etl.load_datasus --strict
```

O modo `--strict` valida as contagens esperadas dos arquivos 2024 incluídos no repositório.

## Pipeline ETL

O ETL converte arquivos `.dbc` para `.dbf`, lê os registros com `dbfread`, normaliza nomes de colunas e carrega os dados no PostgreSQL. A carga é idempotente por ano: ao recarregar o mesmo ano, os registros anteriores daquele ano são substituídos.

Imagem a adicionar:

- `docs/assets/etl-flow.png`

## Consultas

Consultas iniciais:

- `database/queries/01_validacao_carga.sql`: contagens brutas e recorte Porto Alegre.
- `database/queries/02_indicadores_municipio.sql`: incidência por 1.000 nascidos vivos.
- `database/queries/03_desigualdades_prenatal_escolaridade.sql`: escolaridade nos casos sem pré-natal por grupo racial.
- `database/queries/04_qualidade_registros.sql`: percentual de registros ignorados por variável crítica.
- `database/queries/05_incidencia_por_grupo_racial.sql`: incidência estimada por grupo racial materno.
- `database/queries/06_prenatal_por_grupo_racial.sql`: realização de pré-natal por grupo racial materno.
- `database/queries/07_diagnostico_materno_por_grupo_racial.sql`: momento do diagnóstico materno por grupo racial.

Cada nova consulta deve responder uma pergunta analítica explícita e, quando gerar resultado relevante, deve ser documentada neste arquivo e em `docs/README.en.md`.

## Notebooks

Os notebooks devem ficar em `notebooks/analytics/` e responder perguntas analíticas específicas. O notebook de visualização existente permanece como referência inicial do projeto.

Notebooks iniciais:

- `notebooks/analytics/01_overview_sifilis_congenita.ipynb`: panorama do recorte Porto Alegre e incidência geral.
- `notebooks/analytics/02_prenatal_raca_escolaridade.ipynb`: cruzamento entre pré-natal, raça/cor e escolaridade.

## Referência Dos Notebooks

Cada notebook deve ser executado a partir da raiz do repositório ou pelo Google Colab. Ao usar Colab, carregue os dados do repositório e mantenha os caminhos indicados no próprio notebook.

| Notebook | Pergunta principal | Google Colab | Imagem do resultado |
| --- | --- | --- | --- |
| `notebooks/visualizacao_sifilis_congenita_poars.ipynb` | Dentro dos casos de sífilis congênita sem pré-natal em Porto Alegre, como a escolaridade materna se distribui por grupo racial? | [Abrir no Colab](https://colab.research.google.com/github/paduanton/data-insights-visualization/blob/main/notebooks/visualizacao_sifilis_congenita_poars.ipynb) | `outputs/images/graphs/visualizacao_sifilis_congenita_poars_escolaridade_sem_prenatal.png` |
| `notebooks/analytics/01_overview_sifilis_congenita.ipynb` | Qual é o panorama de casos notificados, nascidos vivos e incidência geral em Porto Alegre? | [Abrir no Colab](https://colab.research.google.com/github/paduanton/data-insights-visualization/blob/main/notebooks/analytics/01_overview_sifilis_congenita.ipynb) | `docs/assets/results/overview_sifilis_congenita.png` |
| `notebooks/analytics/02_prenatal_raca_escolaridade.ipynb` | Como pré-natal, raça/cor e escolaridade se combinam nos casos notificados? | [Abrir no Colab](https://colab.research.google.com/github/paduanton/data-insights-visualization/blob/main/notebooks/analytics/02_prenatal_raca_escolaridade.ipynb) | `docs/assets/results/prenatal_raca_escolaridade.png` |

Ao criar um novo notebook, adicione uma nova linha nesta tabela e mantenha a mesma atualização em `docs/README.en.md`. A imagem do resultado deve ser salva em `docs/assets/results/` quando fizer parte da documentação do projeto, ou em `outputs/images/` quando for uma saída operacional do notebook.

## Resultados

Visualização já produzida:

- `outputs/images/graphs/visualizacao_sifilis_congenita_poars_escolaridade_sem_prenatal.png`

Resultados iniciais validados para 2024:

- SINAN/SIFCBR: `12762` registros no Rio Grande do Sul.
- SINASC: `111988` registros no Rio Grande do Sul.
- Porto Alegre: `137` casos de sífilis congênita e `12850` nascidos vivos.
- Incidência geral estimada: `10,66` casos por 1.000 nascidos vivos.
- Casos sem pré-natal: `10` entre mães negras e `14` entre mães não negras.

Imagens de novos resultados devem ser adicionadas em:

- `docs/assets/results/`

Imagem recomendada para o próximo resultado:

- `docs/assets/results/incidencia_por_grupo_racial.png`

## Limitações

- As bases públicas não serão usadas para pareamento individual entre SINAN e SINASC.
- A unidade analítica principal é agregada por município, ano e estratos.
- Categorias ignoradas ou sem informação são preservadas e medidas.
- CNES, SIM, IBGE e outras fontes entram como camadas complementares, não como dependências da primeira carga.
