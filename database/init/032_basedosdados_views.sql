CREATE SCHEMA IF NOT EXISTS silver;
CREATE SCHEMA IF NOT EXISTS gold;

DROP VIEW IF EXISTS gold.contexto_integrado_municipio_ano;
DROP VIEW IF EXISTS gold.populacao_municipio_ano;
DROP VIEW IF EXISTS silver.basedosdados_populacao_municipio;

CREATE VIEW silver.basedosdados_populacao_municipio AS
SELECT
    source_year::integer AS ano,
    NULLIF(TRIM(cod_municipio), '') AS cod_municipio,
    NULLIF(TRIM(id_municipio), '') AS id_municipio,
    NULLIF(TRIM(populacao_residente), '')::bigint AS populacao_residente,
    NULLIF(TRIM(source), '') AS fonte,
    NULLIF(TRIM(source_table), '') AS tabela_origem
FROM bronze.basedosdados_populacao_municipio;

CREATE VIEW gold.populacao_municipio_ano AS
SELECT
    ano,
    cod_municipio,
    SUM(populacao_residente) AS populacao_residente
FROM silver.basedosdados_populacao_municipio
WHERE cod_municipio IS NOT NULL
GROUP BY ano, cod_municipio;

CREATE VIEW gold.contexto_integrado_municipio_ano AS
SELECT
    indicadores.ano,
    indicadores.cod_municipio_residencia AS cod_municipio,
    indicadores.casos_sc,
    indicadores.nascidos_vivos,
    indicadores.incidencia_sc_por_1000_nv,
    populacao.populacao_residente,
    ROUND(
        indicadores.casos_sc::numeric / NULLIF(populacao.populacao_residente, 0) * 100000,
        2
    ) AS casos_sc_por_100000_habitantes,
    cnes.estabelecimentos_distintos,
    cnes.tipos_unidade_distintos,
    sim.obitos_gerais,
    sim.obitos_causa_a50,
    sim.obitos_raca_ignorada
FROM gold.indicadores_municipio_ano AS indicadores
LEFT JOIN gold.populacao_municipio_ano AS populacao
  ON populacao.ano = indicadores.ano
 AND populacao.cod_municipio = indicadores.cod_municipio_residencia
LEFT JOIN gold.cnes_estabelecimentos_municipio_ano AS cnes
  ON cnes.ano = indicadores.ano
 AND cnes.cod_municipio = indicadores.cod_municipio_residencia
LEFT JOIN gold.sim_obitos_municipio_ano AS sim
  ON sim.ano = indicadores.ano
 AND sim.cod_municipio_residencia = indicadores.cod_municipio_residencia;
