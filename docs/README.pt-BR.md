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

Uso no projeto da Base dos Dados:

- `notebooks/analytics/02_auditoria_basedosdados.ipynb` audita disponibilidade, colunas, período e custo estimado via BigQuery.
- `python -m src.etl.audit_basedosdados` gera uma matriz CSV de auditoria em `data/profiles/basedosdados_audit.csv`.
- A implementação principal continua usando microdados DATASUS locais em `.dbc`.
- Base dos Dados é usada para validação cruzada de cobertura, consulta exploratória rápida e enriquecimento contextual com população municipal.
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
- `data/profiles/`: perfis gerados para auditoria de colunas, cobertura e qualidade.

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
- `gold.sintese_desigualdade_racial_municipio_ano`: camada final com razão, diferença absoluta e excesso relativo da incidência.
- `gold.prenatal_grupo_racial_municipio_ano`: distribuição de pré-natal entre casos por grupo racial.
- `gold.diagnostico_materno_grupo_racial_municipio_ano`: momento do diagnóstico materno por grupo racial.
- `gold.tratamento_materno_grupo_racial_municipio_ano`: tratamento materno adequado por grupo racial.
- `gold.qualidade_registros`: ignorados por variável crítica.

Caminho reservado para o diagrama de arquitetura:

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

O comando multi-ano procura arquivos na estrutura histórica consolidada e também preserva fallback para o MVP 2024 atual.

Antes de baixar novos arquivos, gere um inventário:

```bash
python -m src.etl.inventory_datasus --years 2015:2024
```

Para uma lista de download manual, use:

```bash
python -m src.etl.inventory_datasus --years 2015:2024 --missing-only --format markdown --output data/profiles/datasus_missing_files_2015_2024.md
```

Para auditar tabelas candidatas da Base dos Dados:

```bash
python -m src.etl.audit_basedosdados
```

Com `GOOGLE_CLOUD_PROJECT` e credenciais configuradas, o comando estima bytes via BigQuery `dry_run`. Para executar consultas de período, use:

```bash
python -m src.etl.audit_basedosdados --execute
```

As tabelas auditadas podem ser ajustadas no ambiente com as variaveis `BASEDOSDADOS_SINASC_TABLE`, `BASEDOSDADOS_SIM_TABLE`, `BASEDOSDADOS_CNES_TABLE`, `BASEDOSDADOS_POPULACAO_TABLE`, `BASEDOSDADOS_SIH_SERVICOS_TABLE` e `BASEDOSDADOS_SINAN_REFERENCIA_TABLE`.
Os scripts de ETL e auditoria carregam `.env` automaticamente quando o arquivo existir, preservando variaveis ja definidas no terminal.

Para fontes complementares já validadas por profiling, há cargas bronze separadas:

```bash
python -m src.etl.load_cnes --years 2015:2024 --month 12
python -m src.etl.load_sim --years 2015:2024
python -m src.etl.load_basedosdados --years 2015:2024
```

## Pipeline ETL

O ETL converte arquivos `.dbc` para `.dbf`, lê os registros com `dbfread`, normaliza nomes de colunas e carrega os dados no PostgreSQL. A carga é idempotente por ano: ao recarregar o mesmo ano, os registros anteriores daquele ano são substituídos. Nas tabelas `bronze`, colunas novas encontradas em anos posteriores são adicionadas como `TEXT`, preservando variações dos microdados sem quebrar as views analíticas consolidadas.

Caminho reservado para o diagrama do fluxo ETL:

- `docs/assets/etl-flow.png`

Para auditar colunas e qualidade, gere perfis exploratórios:

```bash
python -m src.etl.profile_datasus --years 2015:2024
```

Para incluir fontes complementares no profiling:

```bash
python -m src.etl.profile_datasus --years 2015:2024 --skip-core --include-cnes --output data/profiles/cnes_st_column_profile_2015_2024.csv
python -m src.etl.profile_datasus --years 2015:2024 --skip-core --include-sim --output data/profiles/sim_do_column_profile_2015_2024.csv
```

Os perfis são salvos em `data/profiles/` e permitem revisar colunas, categorias e qualidade das views finais.

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
- `database/queries/13_sintese_desigualdade_racial.sql`: síntese anual da desigualdade racial na incidência de sífilis congênita.
- `database/queries/14_contexto_integrado_municipio.sql`: contexto integrado de incidência, população, CNES e SIM.
- `database/queries/15_tratamento_materno_por_grupo_racial.sql`: tratamento materno adequado por grupo racial.

Cada nova consulta deve responder uma pergunta analítica explícita e, quando gerar resultado relevante, deve ser documentada neste arquivo e em `docs/README.en.md`.

## Notebooks

Os notebooks devem ficar em `notebooks/analytics/` e responder perguntas analíticas específicas. O notebook de visualização existente permanece como referência inicial do projeto.

Notebooks analíticos:

- `notebooks/analytics/00_validacao_ambiente_dados.ipynb`: validação de ambiente, Docker, testes e carga strict.
- `notebooks/analytics/01_overview_sifilis_congenita.ipynb`: panorama do recorte Porto Alegre e incidência geral.
- `notebooks/analytics/02_auditoria_basedosdados.ipynb`: auditoria de cobertura, custo e uso possível da Base dos Dados.
- `notebooks/analytics/03_prenatal_raca_escolaridade.ipynb`: cruzamento entre pré-natal, raça/cor e escolaridade.
- `notebooks/analytics/04_perfil_colunas_qualidade.ipynb`: profiling das colunas e variáveis críticas do schema analítico.
- `notebooks/analytics/05_serie_historica_incidencia.ipynb`: evolução anual da incidência em Porto Alegre.
- `notebooks/analytics/06_desigualdade_racial_incidencia.ipynb`: incidência e razão de incidência por grupo racial.
- `notebooks/analytics/07_diagnostico_tratamento_cuidado.ipynb`: diagnóstico materno e tratamento materno adequado.
- `notebooks/analytics/08_contexto_cnes_ibge_sim.ipynb`: inventário e uso contextual de CNES, IBGE e SIM.
- `notebooks/analytics/09_sintese_desigualdade_racial.ipynb`: camada final de síntese dos indicadores de desigualdade racial.
- `notebooks/analytics/10_contexto_integrado_basedosdados.ipynb`: contexto integrado com população da Base dos Dados, CNES, SIM e incidência.

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
| `notebooks/analytics/07_diagnostico_tratamento_cuidado.ipynb` | Diagnóstico materno e tratamento adequado registrado indicam diferenças no cuidado entre grupos raciais? | [Abrir no Colab](https://colab.research.google.com/github/paduanton/data-insights-visualization/blob/main/notebooks/analytics/07_diagnostico_tratamento_cuidado.ipynb) | `docs/assets/results/tratamento_materno_grupo_racial.png` |
| `notebooks/analytics/08_contexto_cnes_ibge_sim.ipynb` | Quais fontes complementares podem contextualizar oferta assistencial, população e desfechos? | [Abrir no Colab](https://colab.research.google.com/github/paduanton/data-insights-visualization/blob/main/notebooks/analytics/08_contexto_cnes_ibge_sim.ipynb) | `docs/assets/results/contexto_cnes_ibge_sim.png` |
| `notebooks/analytics/09_sintese_desigualdade_racial.ipynb` | A série histórica confirma desigualdade persistente na incidência entre mães negras e mães não negras? | [Abrir no Colab](https://colab.research.google.com/github/paduanton/data-insights-visualization/blob/main/notebooks/analytics/09_sintese_desigualdade_racial.ipynb) | `docs/assets/results/sintese_desigualdade_racial.png` |
| `notebooks/analytics/10_contexto_integrado_basedosdados.ipynb` | Como a incidência de sífilis congênita se posiciona junto ao contexto populacional, assistencial e de mortalidade? | [Abrir no Colab](https://colab.research.google.com/github/paduanton/data-insights-visualization/blob/main/notebooks/analytics/10_contexto_integrado_basedosdados.ipynb) | `docs/assets/results/contexto_integrado_basedosdados.png` |

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
- Base dos Dados/população municipal: `4970` registros agregados para municípios do Rio Grande do Sul, com `497` municípios por ano.
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

Esses resultados confirmam que a base histórica está carregada, consultável e sustentando o schema analítico consolidado para o recorte `2015-2024`.

Perfil decisório das variáveis críticas:

- SINAN/SIFCBR possui campos estáveis para raça/cor materna, pré-natal, escolaridade, diagnóstico materno, tratamento materno adequado e município de residência em `2015-2024`.
- SINASC possui campos estáveis para raça/cor materna, consultas de pré-natal, escolaridade materna e município de residência em `2015-2024`.
- CNES/ST possui campos estáveis para estabelecimento, município, tipo de unidade e atividade no snapshot anual de dezembro.
- SIM/DO possui campos estáveis para município de residência, município de ocorrência, causa básica, data do óbito e raça/cor.
- A escolaridade do SINAN/SIFCBR preserva a categoria detalhada em `escolaridade_mae_detalhada` e usa o agrupamento analítico `00-03` como até 7 anos de estudo, `04-08` como 8 anos ou mais de estudo e `09`, `10` ou vazio como ignorada/sem informação. A regra está documentada em `docs/references/dicionario_escolaridade_sinan.md`.
- Categorias ignoradas, vazias ou sem informação permanecem preservadas e mensuradas nas consultas.

Imagens geradas:

- `docs/assets/results/serie_historica_incidencia.png`
- `docs/assets/results/desigualdade_racial_incidencia.png`
- `docs/assets/results/razao_incidencia_grupo_racial.png`
- `docs/assets/results/diagnostico_materno_grupo_racial.png`
- `docs/assets/results/tratamento_materno_grupo_racial.png`
- `docs/assets/results/contexto_cnes_ibge_sim.png`
- `docs/assets/results/sintese_desigualdade_racial.png`
- `docs/assets/results/perfil_colunas_qualidade.png`
- `docs/assets/results/auditoria_basedosdados_periodos.png`
- `docs/assets/results/contexto_integrado_basedosdados.png`

Leitura da camada final:

- A razão de incidência entre mães negras e mães não negras permanece acima de `1` em todos os anos carregados.
- Em `2024`, a incidência entre mães negras foi `1,54` vez a incidência entre mães não negras, com diferença absoluta de `4,95` casos por 1.000 nascidos vivos.
- Em `2024`, o tratamento materno inadequado foi registrado em `98,2%` dos casos de mães negras e em `85,0%` dos casos de mães não negras em Porto Alegre.
- A queda geral da incidência após `2022` não elimina a desigualdade relativa entre os grupos.
- As análises de pré-natal, escolaridade e diagnóstico materno devem ser lidas como estratos descritivos dos casos notificados, não como pareamento individual nem inferência causal.

Auditoria da Base dos Dados:

- O pacote `basedosdados` está instalado localmente e importável.
- O cliente `google-cloud-bigquery` também está disponível.
- Os IDs BigQuery candidatos estão parametrizados em `.env.example`.
- A auditoria completa foi executada via BigQuery com `dry_run`, limite de bytes e filtros por ano/UF quando disponíveis.
- Períodos auditados: SINASC `1994-2024`, SIM `1996-2024`, CNES `2005-2025`, população municipal `2000-2025`, SIH `2008-2025` e SINAN violência `2009-2019`.
- A população municipal da Base dos Dados foi incorporada como contexto agregado em `gold.contexto_integrado_municipio_ano`; o denominador principal da incidência permanece sendo nascidos vivos do SINASC.
- A camada Base dos Dados ajuda a validar cobertura e enriquecer contexto populacional; ela não substitui os microdados DATASUS usados no cálculo principal da incidência.

## Limitações

- As bases públicas não serão usadas para pareamento individual entre SINAN e SINASC.
- A unidade analítica principal é agregada por município, ano e estratos.
- Categorias ignoradas ou sem informação são preservadas e medidas.
- CNES, SIM, IBGE e outras fontes entram como camadas complementares, não como dependências da primeira carga.
