# Síntese Final Dos Resultados

Este documento consolida os principais resultados do projeto para apoiar o relatório final. A leitura é descritiva, agregada por município, ano e estratos; não há pareamento individual entre SINAN/SIFCBR, SINASC, CNES, SIM ou Base dos Dados.

## Evidência Central

A evidência central do projeto é a persistência de maior incidência estimada de sífilis congênita entre mães negras em Porto Alegre, RS, Brasil, ao longo de toda a série `2015-2024`.

O numerador da incidência é o SINAN/SIFCBR, porque ele registra os casos notificados de sífilis congênita. O denominador é o SINASC/DNRS, porque o indicador epidemiológico principal é calculado por `1.000 nascidos vivos`, não por população residente geral.

Em `2024`, a incidência entre mães negras foi `1,54` vez a incidência entre mães não negras, com diferença absoluta de `4,95` casos por `1.000` nascidos vivos.

## Resultados Principais

- A razão de incidência entre mães negras e mães não negras permaneceu acima de `1` em todos os anos carregados.
- A série geral de Porto Alegre foi validada para `2015-2024` em `gold.indicadores_municipio_ano`.
- Em `2024`, Porto Alegre teve `137` casos de sífilis congênita e `12850` nascidos vivos, com incidência geral de `10,66` por `1.000` nascidos vivos.
- Em `2024`, o tratamento materno inadequado foi registrado em `98,2%` dos casos de mães negras e `85,0%` dos casos de mães não negras.
- A análise interseccional mostrou marcador de maior vulnerabilidade em `44,8%` dos casos de mães negras (`n=791`) e `40,3%` dos casos de mães não negras (`n=1023`).

## Resultados Complementares

- A análise por raça/cor detalhada complementa a leitura principal: preta e parda aparecem com incidências superiores à branca na maior parte da série.
- Categorias amarela, indígena e ignorada têm denominadores baixos ou instáveis em Porto Alegre e devem ser interpretadas como exploração complementar.
- CNES, SIM e população municipal entram como contexto agregado, não como base de cálculo do indicador principal.
- Base dos Dados foi usada para auditoria, validação de cobertura e contexto populacional agregado.

## Gráficos Gerados

Resultados em `docs/assets/results/`:

- `docs/assets/results/overview_sifilis_congenita.png`
- `docs/assets/results/serie_historica_incidencia.png`
- `docs/assets/results/desigualdade_racial_incidencia.png`
- `docs/assets/results/razao_incidencia_grupo_racial.png`
- `docs/assets/results/diagnostico_materno_grupo_racial.png`
- `docs/assets/results/tratamento_materno_grupo_racial.png`
- `docs/assets/results/contexto_cnes_ibge_sim.png`
- `docs/assets/results/sintese_desigualdade_racial.png`
- `docs/assets/results/contexto_integrado_basedosdados.png`

Imagens finais em `outputs/images/final_report/`:

- `outputs/images/final_report/incidencia_grupo_racial_ano.png`
- `outputs/images/final_report/razao_incidencia_racial.png`
- `outputs/images/final_report/incidencia_raca_cor_detalhada.png`
- `outputs/images/final_report/prenatal_grupo_racial.png`
- `outputs/images/final_report/diagnostico_materno_grupo_racial.png`
- `outputs/images/final_report/tratamento_materno_grupo_racial.png`
- `outputs/images/final_report/perfil_maes_negras_escolaridade_idade.png`
- `outputs/images/final_report/analise_interseccional_desigualdade.png`
- `outputs/images/final_report/qualidade_dados_ignorados.png`

## Notebooks Associados

- `notebooks/analytics/05_serie_historica_incidencia.ipynb`: incidência geral.
- `notebooks/analytics/06_desigualdade_racial_incidencia.ipynb`: incidência por grupo racial.
- `notebooks/analytics/07_diagnostico_tratamento_cuidado.ipynb`: diagnóstico materno e tratamento.
- `notebooks/analytics/09_sintese_desigualdade_racial.ipynb`: síntese anual da desigualdade racial.
- `notebooks/11_analise_interseccional_desigualdade.ipynb`: raça/cor detalhada, perfil e interseccionalidade.
- `notebooks/12_relatorio_final_consolidado.ipynb`: organização dos resultados finais.

## Qualidade Dos Dados

Categorias ignoradas, vazias ou sem informação foram preservadas e mensuradas. Elas não foram descartadas silenciosamente.

Em Porto Alegre, no período `2015-2024`, os maiores percentuais de ignorados nas variáveis críticas foram:

- SINAN/SIFCBR `escolaridade_mae`: `31,8%`;
- SINAN/SIFCBR `tratamento_materno_adequado`: `29,8%`;
- SINAN/SIFCBR `raca_cor_mae`: `10,6%`;
- SINAN/SIFCBR `pre_natal`: `3,3%`;
- SINASC `consultas_prenatal`: `0,1%`;
- SINASC `raca_cor_mae`: `0,0%`.

## Limitações

- A análise é agregada e descritiva.
- Não há linkage individual entre SINAN/SIFCBR e SINASC.
- Não há inferência causal.
- Não é possível inferir UBS de atendimento a partir dos dados usados.
- População residente geral não é denominador do indicador principal.
- Categorias com baixo denominador, especialmente amarela, indígena e ignorada na análise detalhada por raça/cor, devem ser interpretadas com cautela.
- Diferenças observadas podem refletir desigualdades sociais, assistenciais e de registro, mas o desenho atual não estima causalidade.

## Interpretação Prática Para O Relatório

O resultado mais robusto para sustentar a argumentação é a série histórica de incidência por grupo racial. As análises de pré-natal, diagnóstico, tratamento, escolaridade e perfil materno qualificam a leitura ao mostrar dimensões de cuidado e vulnerabilidade associadas aos casos notificados.

Para o relatório final, recomenda-se apresentar primeiro a incidência e a razão de incidência, depois os marcadores de cuidado, e por fim a análise interseccional e a qualidade dos dados como camadas interpretativas.
