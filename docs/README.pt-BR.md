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

- `data/raw/sinan/sifilis_congenita/SIFCBR15.dbc` a `data/raw/sinan/sifilis_congenita/SIFCBR24.dbc`: SINAN/SIFCBR 2015-2024, notificações de sífilis congênita.
- `data/raw/sinasc/DNRS2015.dbc` a `data/raw/sinasc/DNRS2024.dbc`: SINASC 2015-2024, nascidos vivos no Rio Grande do Sul.

Fontes preservadas para expansão:

- `data/raw/cnes/st/STRS1512.dbc` a `data/raw/cnes/st/STRS2412.dbc`: CNES/ST, dezembro de cada ano como snapshot anual.
- `data/raw/cnes/ep/` e `data/raw/cnes/sr/`: CNES complementar, também filtrado para dezembro de 2015-2024.
- `data/raw/sim/do/DORS2015.dbc` a `data/raw/sim/do/DORS2024.dbc`: SIM 2015-2024, óbitos gerais.
- `data/raw/sim/dofet/`, `data/raw/sim/doinf/` e `data/raw/sim/domat/`: SIM complementar.
- `data/raw/populacao_datasus/`: população DATASUS/IBGE complementar.

Fonte auxiliar para inventário e validação:

- Base dos Dados via `basedosdados` e `google-cloud-bigquery`, com auditoria de tabelas BigQuery úteis para SINASC, SIM, CNES, população municipal, SIH e referência técnica SINAN.

Uso previsto da Base dos Dados:

- `notebooks/analytics/02_auditoria_basedosdados.ipynb` audita disponibilidade, colunas, período e custo estimado via BigQuery.
- A implementação principal continua usando microdados DATASUS locais em `.dbc`.
- Base dos Dados pode ser usada para validação cruzada de totais, consulta exploratória rápida e enriquecimento contextual quando a cobertura e o custo forem adequados.
- Não deve substituir automaticamente DATASUS/IBGE como fonte primária documentada do pipeline.

Estrutura para consolidação histórica:

- `data/raw/sinan/sifilis_congenita/`: arquivos `SIFCBR*.dbc`.
- `data/raw/sinasc/`: arquivos `DNRS*.dbc`.
- `data/raw/cnes/st/`: arquivos CNES `STRS*.dbc`.
- `data/raw/cnes/ep/` e `data/raw/cnes/sr/`: arquivos CNES complementares de dezembro.
- `data/raw/sim/do/`: arquivos SIM `DORS*.dbc`.
- `data/raw/populacao_datasus/`: arquivos populacionais complementares.
- `data/ignored/`: arquivos preservados fora do recorte principal.
- `data/staging/`: conversões exploratórias.
- `data/profiles/`: perfis gerados antes do schema final.

Inventário consolidado da janela `2015-2024`:

- `docs/inventario_bases.md`: cobertura principal, CNES selecionado e resumo de arquivos preservados/ignorados.
- `data/profiles/datasus_file_inventory.csv`: inventário detalhado gerado localmente.

Para verificar arquivos ausentes no recorte atual:

```bash
python -m src.etl.inventory_datasus --years 2015:2024 --missing-only --output data/profiles/datasus_missing_files_2015_2024.csv
```

Para regenerar o inventário detalhado:

```bash
python -m src.etl.inventory_datasus --years 2015:2024 --scan-files --output data/profiles/datasus_file_inventory.csv --docs-output docs/inventario_bases.md
```

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

Views analíticas consolidadas:

- `gold.indicadores_municipio_ano`: casos, nascidos vivos e incidência geral por município/ano.
- `gold.incidencia_grupo_racial_municipio_ano`: incidência estimada por grupo racial materno.
- `gold.razao_incidencia_grupo_racial_municipio_ano`: razão de incidência entre mães negras e mães não negras.
- `gold.prenatal_grupo_racial_municipio_ano`: distribuição de pré-natal entre casos por grupo racial.
- `gold.diagnostico_materno_grupo_racial_municipio_ano`: momento do diagnóstico materno por grupo racial.
- `gold.qualidade_registros`: ignorados por variável crítica.

Imagem a adicionar:

- `docs/assets/architecture.png`

## Execução Local

Suba o PostgreSQL:

```bash
docker compose up -d
```

O PgAdmin fica disponível em `http://localhost:5050`. Use as credenciais de `PGADMIN_DEFAULT_EMAIL` e `PGADMIN_DEFAULT_PASSWORD` definidas no `.env`; os valores padrão do `.env.example` são `admin@example.com` e `admin`.

Para registrar o banco no PgAdmin, use:

- host: `postgres`
- porta: `5432`
- database: `sifilis_analytics`
- usuário: `postgres`
- senha: `postgres`

Instale as dependências:

```bash
python -m pip install -r requirements.txt
```

Execute a carga:

```bash
python -m src.etl.load_datasus --strict
```

O modo `--strict` valida as contagens esperadas dos arquivos 2024 incluídos no repositório.

Para carga multi-ano, use:

```bash
python -m src.etl.load_datasus --years 2015:2024
```

O comando multi-ano procura arquivos na estrutura histórica planejada e também preserva fallback para o MVP 2024 atual.

Antes de baixar novos arquivos, gere um inventário:

```bash
python -m src.etl.inventory_datasus --years 2015:2024
```

Para uma lista de download manual, use:

```bash
python -m src.etl.inventory_datasus --years 2015:2024 --missing-only --format markdown --output data/profiles/datasus_missing_files_2015_2024.md
```

Para fontes complementares já validadas por profiling, há cargas bronze separadas:

```bash
python -m src.etl.load_cnes --years 2015:2024 --month 12
python -m src.etl.load_sim --years 2015:2024
```

## Pipeline ETL

O ETL converte arquivos `.dbc` para `.dbf`, lê os registros com `dbfread`, normaliza nomes de colunas e carrega os dados no PostgreSQL. A carga é idempotente por ano: ao recarregar o mesmo ano, os registros anteriores daquele ano são substituídos. Nas tabelas `bronze`, colunas novas encontradas em anos posteriores são adicionadas como `TEXT`, preservando variações dos microdados até a decisão do schema final.

Imagem a adicionar:

- `docs/assets/etl-flow.png`

Antes do schema analítico final, gere perfis exploratórios:

```bash
python -m src.etl.profile_datasus --years 2015:2024
```

Para incluir fontes complementares no profiling:

```bash
python -m src.etl.profile_datasus --years 2015:2024 --skip-core --include-cnes --output data/profiles/cnes_st_column_profile_2015_2024.csv
python -m src.etl.profile_datasus --years 2015:2024 --skip-core --include-sim --output data/profiles/sim_do_column_profile_2015_2024.csv
```

Os perfis são salvos em `data/profiles/` e devem orientar a decisão de colunas, categorias e views finais.

## Consultas

Consultas iniciais:

- `database/queries/01_validacao_carga.sql`: contagens brutas e recorte Porto Alegre.
- `database/queries/02_indicadores_municipio.sql`: incidência por 1.000 nascidos vivos.
- `database/queries/03_desigualdades_prenatal_escolaridade.sql`: escolaridade nos casos sem pré-natal por grupo racial.
- `database/queries/04_qualidade_registros.sql`: percentual de registros ignorados por variável crítica.
- `database/queries/05_incidencia_por_grupo_racial.sql`: incidência estimada por grupo racial materno.
- `database/queries/06_prenatal_por_grupo_racial.sql`: realização de pré-natal por grupo racial materno.
- `database/queries/07_diagnostico_materno_por_grupo_racial.sql`: momento do diagnóstico materno por grupo racial.
- `database/queries/08_razao_incidencia_grupo_racial.sql`: razão de incidência entre mães negras e mães não negras.
- `database/queries/09_inventario_campos_cuidado_materno.sql`: inspeção de campos candidatos para pré-natal, diagnóstico, tratamento, escolaridade, idade e raça/cor.
- `database/queries/10_contexto_cnes_municipio.sql`: contexto anual de estabelecimentos CNES por município.
- `database/queries/11_contexto_sim_municipio.sql`: óbitos gerais e causa básica `A50` no SIM por município de residência.
- `database/queries/12_perfil_variaveis_criticas.sql`: distribuição de códigos brutos, categorias analíticas e percentuais das variáveis críticas.

Cada nova consulta deve responder uma pergunta analítica explícita e, quando gerar resultado relevante, deve ser documentada neste arquivo e em `docs/README.en.md`.

## Notebooks

Os notebooks devem ficar em `notebooks/analytics/` e responder perguntas analíticas específicas. O notebook de visualização existente permanece como referência inicial do projeto.

Notebooks iniciais:

- `notebooks/analytics/00_validacao_ambiente_dados.ipynb`: validação de ambiente, Docker, testes e carga strict.
- `notebooks/analytics/01_overview_sifilis_congenita.ipynb`: panorama do recorte Porto Alegre e incidência geral.
- `notebooks/analytics/02_auditoria_basedosdados.ipynb`: auditoria de cobertura, custo e uso possível da Base dos Dados.
- `notebooks/analytics/03_prenatal_raca_escolaridade.ipynb`: cruzamento entre pré-natal, raça/cor e escolaridade.
- `notebooks/analytics/04_perfil_colunas_qualidade.ipynb`: profiling das colunas e variáveis críticas antes do schema final.
- `notebooks/analytics/05_serie_historica_incidencia.ipynb`: evolução anual da incidência em Porto Alegre.
- `notebooks/analytics/06_desigualdade_racial_incidencia.ipynb`: incidência e razão de incidência por grupo racial.
- `notebooks/analytics/07_diagnostico_tratamento_cuidado.ipynb`: diagnóstico materno e base para análise de tratamento.
- `notebooks/analytics/08_contexto_cnes_ibge_sim.ipynb`: inventário e uso contextual de CNES, IBGE e SIM.

## Referência Dos Notebooks

Cada notebook deve ser executado a partir da raiz do repositório ou pelo Google Colab. Ao usar Colab, carregue os dados do repositório e mantenha os caminhos indicados no próprio notebook.

| Notebook | Pergunta principal | Google Colab | Imagem do resultado |
| --- | --- | --- | --- |
| `notebooks/visualizacao_sifilis_congenita_poars.ipynb` | Dentro dos casos de sífilis congênita sem pré-natal em Porto Alegre, como a escolaridade materna se distribui por grupo racial? | [Abrir no Colab](https://colab.research.google.com/github/paduanton/data-insights-visualization/blob/main/notebooks/visualizacao_sifilis_congenita_poars.ipynb) | `outputs/images/graphs/visualizacao_sifilis_congenita_poars_escolaridade_sem_prenatal.png` |
| `notebooks/analytics/00_validacao_ambiente_dados.ipynb` | O ambiente consegue reproduzir o MVP 2024 antes da expansão histórica? | [Abrir no Colab](https://colab.research.google.com/github/paduanton/data-insights-visualization/blob/main/notebooks/analytics/00_validacao_ambiente_dados.ipynb) | `docs/assets/results/validacao_ambiente_dados.png` |
| `notebooks/analytics/01_overview_sifilis_congenita.ipynb` | Qual é o panorama de casos notificados, nascidos vivos e incidência geral em Porto Alegre? | [Abrir no Colab](https://colab.research.google.com/github/paduanton/data-insights-visualization/blob/main/notebooks/analytics/01_overview_sifilis_congenita.ipynb) | `docs/assets/results/overview_sifilis_congenita.png` |
| `notebooks/analytics/02_auditoria_basedosdados.ipynb` | Quais tabelas da Base dos Dados podem complementar ou validar as bases DATASUS do projeto? | [Abrir no Colab](https://colab.research.google.com/github/paduanton/data-insights-visualization/blob/main/notebooks/analytics/02_auditoria_basedosdados.ipynb) | `docs/assets/results/auditoria_basedosdados_periodos.png` |
| `notebooks/analytics/03_prenatal_raca_escolaridade.ipynb` | Como pré-natal, raça/cor e escolaridade se combinam nos casos notificados? | [Abrir no Colab](https://colab.research.google.com/github/paduanton/data-insights-visualization/blob/main/notebooks/analytics/03_prenatal_raca_escolaridade.ipynb) | `docs/assets/results/prenatal_raca_escolaridade.png` |
| `notebooks/analytics/04_perfil_colunas_qualidade.ipynb` | Quais colunas e variáveis críticas sustentam o schema analítico final? | [Abrir no Colab](https://colab.research.google.com/github/paduanton/data-insights-visualization/blob/main/notebooks/analytics/04_perfil_colunas_qualidade.ipynb) | `docs/assets/results/perfil_colunas_qualidade.png` |
| `notebooks/analytics/05_serie_historica_incidencia.ipynb` | Como a incidência de sífilis congênita evolui nos anos carregados? | [Abrir no Colab](https://colab.research.google.com/github/paduanton/data-insights-visualization/blob/main/notebooks/analytics/05_serie_historica_incidencia.ipynb) | `docs/assets/results/serie_historica_incidencia.png` |
| `notebooks/analytics/06_desigualdade_racial_incidencia.ipynb` | A incidência estimada difere entre mães negras e mães não negras? | [Abrir no Colab](https://colab.research.google.com/github/paduanton/data-insights-visualization/blob/main/notebooks/analytics/06_desigualdade_racial_incidencia.ipynb) | `docs/assets/results/desigualdade_racial_incidencia.png` |
| `notebooks/analytics/07_diagnostico_tratamento_cuidado.ipynb` | O momento do diagnóstico materno indica diferenças no cuidado registrado? | [Abrir no Colab](https://colab.research.google.com/github/paduanton/data-insights-visualization/blob/main/notebooks/analytics/07_diagnostico_tratamento_cuidado.ipynb) | `docs/assets/results/diagnostico_materno_grupo_racial.png` |
| `notebooks/analytics/08_contexto_cnes_ibge_sim.ipynb` | Quais fontes complementares podem contextualizar oferta assistencial, população e desfechos? | [Abrir no Colab](https://colab.research.google.com/github/paduanton/data-insights-visualization/blob/main/notebooks/analytics/08_contexto_cnes_ibge_sim.ipynb) | `docs/assets/results/contexto_cnes_ibge_sim.png` |

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

Consolidação histórica validada no PostgreSQL para `2015-2024`:

- SINAN/SIFCBR: `233882` notificações no Rio Grande do Sul.
- SINASC: `1315073` nascidos vivos no Rio Grande do Sul.
- CNES/ST: `287630` registros de estabelecimentos, usando dezembro como snapshot anual.
- SIM/DO: `943634` registros de óbitos gerais no Rio Grande do Sul.
- Porto Alegre possui série anual de incidência calculada em `gold.indicadores_municipio_ano`.

Série validada para Porto Alegre:

| Ano | Casos | Nascidos vivos | Incidência por 1.000 NV |
| --- | ---: | ---: | ---: |
| 2015 | 593 | 19724 | 30,06 |
| 2016 | 569 | 18635 | 30,53 |
| 2017 | 610 | 18490 | 32,99 |
| 2018 | 513 | 17579 | 29,18 |
| 2019 | 444 | 16520 | 26,88 |
| 2020 | 466 | 15687 | 29,71 |
| 2021 | 632 | 14153 | 44,65 |
| 2022 | 544 | 13679 | 39,77 |
| 2023 | 307 | 13663 | 22,47 |
| 2024 | 137 | 12850 | 10,66 |

Esses resultados confirmam que a base histórica está carregada e consultável, mas o schema analítico final ainda deve ser fechado após leitura dos perfis de colunas e qualidade.

Perfil decisório das variáveis críticas:

- SINAN/SIFCBR possui campos estáveis para raça/cor materna, pré-natal, escolaridade, diagnóstico materno e município de residência em `2015-2024`.
- SINASC possui campos estáveis para raça/cor materna, consultas de pré-natal, escolaridade materna e município de residência em `2015-2024`.
- CNES/ST possui campos estáveis para estabelecimento, município, tipo de unidade e atividade no snapshot anual de dezembro.
- SIM/DO possui campos estáveis para município de residência, município de ocorrência, causa básica, data do óbito e raça/cor.
- A escolaridade do SINAN/SIFCBR deve ser revisada com dicionário oficial antes de refinar categorias finais, porque códigos como `00`, `01` e `10` existem no período histórico e atualmente entram como `Ignorada/sem informacao`.
- Categorias ignoradas, vazias ou sem informação permanecem preservadas e mensuradas nas consultas.

Imagens geradas:

- `docs/assets/results/serie_historica_incidencia.png`
- `docs/assets/results/desigualdade_racial_incidencia.png`
- `docs/assets/results/razao_incidencia_grupo_racial.png`
- `docs/assets/results/diagnostico_materno_grupo_racial.png`
- `docs/assets/results/contexto_cnes_ibge_sim.png`

Imagens pendentes de geração:

- `docs/assets/results/auditoria_basedosdados_periodos.png`
- `docs/assets/results/perfil_colunas_qualidade.png`

## Limitações

- As bases públicas não serão usadas para pareamento individual entre SINAN e SINASC.
- A unidade analítica principal é agregada por município, ano e estratos.
- Categorias ignoradas ou sem informação são preservadas e medidas.
- CNES, SIM, IBGE e outras fontes entram como camadas complementares, não como dependências da primeira carga.
