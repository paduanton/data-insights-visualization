# Anteprojeto Vs Implementação

Este documento compara a proposta conceitual preservada em `docs/references/anteprojeto_sifilis_congenita_poars.pdf` com a implementação técnica atual do projeto.

## Previsto No Anteprojeto

- Analisar sífilis congênita em Porto Alegre.
- Usar dados públicos de saúde.
- Investigar desigualdades associadas a raça/cor materna e marcadores sociais.
- Produzir resultados visuais para apoiar a interpretação.
- Considerar fontes como SINAN, SINASC, CNES e SIM.
- Inicialmente, avaliar visualização em Power BI.

## Implementado

- Pipeline Python para inventário, profiling, carga e validação.
- PostgreSQL com camadas `bronze`, `silver` e `gold`.
- Docker Compose com PostgreSQL e pgAdmin.
- Carga histórica `2015-2024` de SINAN/SIFCBR e SINASC.
- Carga complementar de CNES/ST, SIM/DO e população municipal.
- Auditoria de Base dos Dados via `basedosdados` e `google-cloud-bigquery`.
- Consultas SQL versionadas em `database/queries/`.
- Notebooks analíticos e notebooks finais de consolidação.
- Imagens finais exportadas em `outputs/images/final_report/`.
- Documentação técnica em português e inglês.

## Mudanças De Escopo

Power BI foi substituído por notebooks, imagens exportadas e documentação técnica porque essa estrutura é mais reprodutível dentro do repositório, permite auditar queries e preserva a conexão direta entre dados, código e resultado visual.

CNES, SIM e população geral ficaram como camadas complementares porque não sustentam o indicador principal de incidência de sífilis congênita. Elas ajudam a contextualizar rede assistencial, mortalidade e população, mas não substituem SINAN/SIFCBR e SINASC.

## Denominador Principal

O denominador principal é o SINASC porque o indicador epidemiológico usado é incidência de sífilis congênita por `1.000 nascidos vivos`.

População residente geral pode contextualizar o município, mas não é o denominador adequado para esse indicador.

## Numerador Principal

O numerador principal é o SINAN/SIFCBR porque ele contém as notificações de sífilis congênita.

As consultas agregam casos por município, ano e estratos, sem tentar ligar indivíduos entre bases.

## Linkage Individual

Não foi feito linkage individual entre SINAN/SIFCBR e SINASC porque o projeto trabalha com microdados públicos, sem necessidade de identificar indivíduos, e porque a unidade analítica segura definida foi município-ano-estrato.

Essa decisão evita inferências indevidas e mantém o foco em indicadores agregados.

## Fontes Complementares

- CNES/ST: contexto anual da rede de estabelecimentos, usando dezembro como snapshot.
- SIM/DO: mortalidade agregada e causa básica `A50` como camada complementar.
- Base dos Dados: auditoria, validação de cobertura e população municipal agregada.
- População municipal: contexto demográfico, sem substituir nascidos vivos.

## Adaptações Técnicas Necessárias

- Conversão de arquivos `.dbc` via Python.
- Padronização de códigos de raça/cor, pré-natal, escolaridade, diagnóstico e tratamento.
- Preservação de categorias ignoradas e sem informação.
- Criação de views `silver` e `gold` para manter bronze flexível.
- Ajuste de visualizações para evitar legendas sobrepostas e interpretações ambíguas.
- Separação entre resultados centrais e complementares.

## Papel Do Agente Executor De Código

O agente executor apoiou a implementação incremental: organização de dados, criação de ETL, ajustes SQL, notebooks, geração de imagens, validações e documentação. As mudanças foram realizadas no repositório com comandos reprodutíveis e verificações locais.

## Resultado Atual

O projeto final entrega uma análise técnica reprodutível sobre desigualdades raciais na sífilis congênita em Porto Alegre, sustentada por banco analítico, consultas SQL, notebooks, gráficos exportados e documentação bilíngue.
