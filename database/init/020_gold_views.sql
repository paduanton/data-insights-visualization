CREATE SCHEMA IF NOT EXISTS gold;

DROP VIEW IF EXISTS gold.razao_incidencia_grupo_racial_municipio_ano;
DROP VIEW IF EXISTS gold.incidencia_grupo_racial_municipio_ano;
DROP VIEW IF EXISTS gold.diagnostico_materno_grupo_racial_municipio_ano;
DROP VIEW IF EXISTS gold.prenatal_grupo_racial_municipio_ano;
DROP VIEW IF EXISTS gold.qualidade_registros;
DROP VIEW IF EXISTS gold.sinasc_nv_ano_raca;
DROP VIEW IF EXISTS gold.sinan_sc_sem_prenatal_escolaridade;
DROP VIEW IF EXISTS gold.sinan_sc_ano_prenatal;
DROP VIEW IF EXISTS gold.sinan_sc_ano_raca;
DROP VIEW IF EXISTS gold.indicadores_municipio_ano;

CREATE VIEW gold.indicadores_municipio_ano AS
WITH casos AS (
    SELECT ano, cod_municipio_residencia, COUNT(*) AS casos_sc
    FROM silver.sinan_sifilis_congenita
    GROUP BY ano, cod_municipio_residencia
),
nascidos AS (
    SELECT ano, cod_municipio_residencia, COUNT(*) AS nascidos_vivos
    FROM silver.sinasc_nascidos_vivos
    GROUP BY ano, cod_municipio_residencia
)
SELECT
    COALESCE(casos.ano, nascidos.ano) AS ano,
    COALESCE(casos.cod_municipio_residencia, nascidos.cod_municipio_residencia) AS cod_municipio_residencia,
    COALESCE(casos.casos_sc, 0) AS casos_sc,
    COALESCE(nascidos.nascidos_vivos, 0) AS nascidos_vivos,
    ROUND(
        COALESCE(casos.casos_sc, 0)::numeric / NULLIF(nascidos.nascidos_vivos, 0) * 1000,
        2
    ) AS incidencia_sc_por_1000_nv
FROM casos
FULL OUTER JOIN nascidos
    ON casos.ano = nascidos.ano
   AND casos.cod_municipio_residencia = nascidos.cod_municipio_residencia;

CREATE VIEW gold.sinan_sc_ano_raca AS
SELECT
    ano,
    cod_municipio_residencia,
    grupo_racial_mae,
    raca_cor_mae,
    COUNT(*) AS casos_sc
FROM silver.sinan_sifilis_congenita
GROUP BY ano, cod_municipio_residencia, grupo_racial_mae, raca_cor_mae;

CREATE VIEW gold.sinan_sc_ano_prenatal AS
SELECT
    ano,
    cod_municipio_residencia,
    grupo_racial_mae,
    realizacao_prenatal,
    COUNT(*) AS casos_sc
FROM silver.sinan_sifilis_congenita
GROUP BY ano, cod_municipio_residencia, grupo_racial_mae, realizacao_prenatal;

CREATE VIEW gold.sinan_sc_sem_prenatal_escolaridade AS
SELECT
    ano,
    cod_municipio_residencia,
    grupo_racial_mae,
    escolaridade_mae,
    COUNT(*) AS casos_sc
FROM silver.sinan_sifilis_congenita
WHERE realizacao_prenatal = 'Sem pre-natal'
GROUP BY ano, cod_municipio_residencia, grupo_racial_mae, escolaridade_mae;

CREATE VIEW gold.sinasc_nv_ano_raca AS
SELECT
    ano,
    cod_municipio_residencia,
    grupo_racial_mae,
    raca_cor_mae,
    COUNT(*) AS nascidos_vivos
FROM silver.sinasc_nascidos_vivos
GROUP BY ano, cod_municipio_residencia, grupo_racial_mae, raca_cor_mae;

CREATE VIEW gold.incidencia_grupo_racial_municipio_ano AS
WITH casos AS (
    SELECT
        ano,
        cod_municipio_residencia,
        grupo_racial_mae,
        SUM(casos_sc) AS casos_sc
    FROM gold.sinan_sc_ano_raca
    GROUP BY ano, cod_municipio_residencia, grupo_racial_mae
),
nascidos AS (
    SELECT
        ano,
        cod_municipio_residencia,
        grupo_racial_mae,
        SUM(nascidos_vivos) AS nascidos_vivos
    FROM gold.sinasc_nv_ano_raca
    GROUP BY ano, cod_municipio_residencia, grupo_racial_mae
)
SELECT
    COALESCE(casos.ano, nascidos.ano) AS ano,
    COALESCE(casos.cod_municipio_residencia, nascidos.cod_municipio_residencia) AS cod_municipio_residencia,
    COALESCE(casos.grupo_racial_mae, nascidos.grupo_racial_mae) AS grupo_racial_mae,
    COALESCE(casos.casos_sc, 0) AS casos_sc,
    COALESCE(nascidos.nascidos_vivos, 0) AS nascidos_vivos,
    ROUND(
        COALESCE(casos.casos_sc, 0)::numeric / NULLIF(nascidos.nascidos_vivos, 0) * 1000,
        2
    ) AS incidencia_sc_por_1000_nv
FROM casos
FULL OUTER JOIN nascidos
    ON nascidos.ano = casos.ano
   AND nascidos.cod_municipio_residencia = casos.cod_municipio_residencia
   AND nascidos.grupo_racial_mae = casos.grupo_racial_mae;

CREATE VIEW gold.razao_incidencia_grupo_racial_municipio_ano AS
SELECT
    negras.ano,
    negras.cod_municipio_residencia,
    negras.casos_sc AS casos_maes_negras,
    negras.nascidos_vivos AS nascidos_vivos_maes_negras,
    negras.incidencia_sc_por_1000_nv AS incidencia_maes_negras,
    nao_negras.casos_sc AS casos_maes_nao_negras,
    nao_negras.nascidos_vivos AS nascidos_vivos_maes_nao_negras,
    nao_negras.incidencia_sc_por_1000_nv AS incidencia_maes_nao_negras,
    ROUND(
        negras.incidencia_sc_por_1000_nv / NULLIF(nao_negras.incidencia_sc_por_1000_nv, 0),
        2
    ) AS razao_incidencia_negras_sobre_nao_negras
FROM gold.incidencia_grupo_racial_municipio_ano AS negras
JOIN gold.incidencia_grupo_racial_municipio_ano AS nao_negras
  ON nao_negras.ano = negras.ano
 AND nao_negras.cod_municipio_residencia = negras.cod_municipio_residencia
WHERE negras.grupo_racial_mae = 'Maes negras'
  AND nao_negras.grupo_racial_mae = 'Maes nao negras';

CREATE VIEW gold.prenatal_grupo_racial_municipio_ano AS
SELECT
    ano,
    cod_municipio_residencia,
    grupo_racial_mae,
    realizacao_prenatal,
    casos_sc,
    ROUND(
        casos_sc::numeric / NULLIF(SUM(casos_sc) OVER (PARTITION BY ano, cod_municipio_residencia, grupo_racial_mae), 0) * 100,
        1
    ) AS percentual_no_grupo
FROM gold.sinan_sc_ano_prenatal;

CREATE VIEW gold.diagnostico_materno_grupo_racial_municipio_ano AS
SELECT
    ano,
    cod_municipio_residencia,
    grupo_racial_mae,
    momento_diagnostico_materno,
    COUNT(*) AS casos_sc,
    ROUND(
        COUNT(*)::numeric / NULLIF(SUM(COUNT(*)) OVER (PARTITION BY ano, cod_municipio_residencia, grupo_racial_mae), 0) * 100,
        1
    ) AS percentual_no_grupo
FROM silver.sinan_sifilis_congenita
GROUP BY ano, cod_municipio_residencia, grupo_racial_mae, momento_diagnostico_materno;

CREATE VIEW gold.qualidade_registros AS
SELECT
    'SINAN/SIFCBR' AS base,
    ano,
    cod_municipio_residencia,
    'raca_cor_mae' AS variavel,
    COUNT(*) FILTER (WHERE grupo_racial_mae = 'Ignorado/sem informacao') AS ignorados,
    COUNT(*) AS total,
    ROUND(COUNT(*) FILTER (WHERE grupo_racial_mae = 'Ignorado/sem informacao')::numeric / NULLIF(COUNT(*), 0) * 100, 2) AS percentual_ignorado
FROM silver.sinan_sifilis_congenita
GROUP BY ano, cod_municipio_residencia
UNION ALL
SELECT
    'SINAN/SIFCBR',
    ano,
    cod_municipio_residencia,
    'pre_natal',
    COUNT(*) FILTER (WHERE realizacao_prenatal = 'Ignorado/sem informacao'),
    COUNT(*),
    ROUND(COUNT(*) FILTER (WHERE realizacao_prenatal = 'Ignorado/sem informacao')::numeric / NULLIF(COUNT(*), 0) * 100, 2)
FROM silver.sinan_sifilis_congenita
GROUP BY ano, cod_municipio_residencia
UNION ALL
SELECT
    'SINAN/SIFCBR',
    ano,
    cod_municipio_residencia,
    'escolaridade_mae',
    COUNT(*) FILTER (WHERE escolaridade_mae = 'Ignorada/sem informacao'),
    COUNT(*),
    ROUND(COUNT(*) FILTER (WHERE escolaridade_mae = 'Ignorada/sem informacao')::numeric / NULLIF(COUNT(*), 0) * 100, 2)
FROM silver.sinan_sifilis_congenita
GROUP BY ano, cod_municipio_residencia
UNION ALL
SELECT
    'SINASC',
    ano,
    cod_municipio_residencia,
    'raca_cor_mae',
    COUNT(*) FILTER (WHERE grupo_racial_mae = 'Ignorado/sem informacao'),
    COUNT(*),
    ROUND(COUNT(*) FILTER (WHERE grupo_racial_mae = 'Ignorado/sem informacao')::numeric / NULLIF(COUNT(*), 0) * 100, 2)
FROM silver.sinasc_nascidos_vivos
GROUP BY ano, cod_municipio_residencia
UNION ALL
SELECT
    'SINASC',
    ano,
    cod_municipio_residencia,
    'consultas_prenatal',
    COUNT(*) FILTER (WHERE consultas_prenatal = 'Ignorado/sem informacao'),
    COUNT(*),
    ROUND(COUNT(*) FILTER (WHERE consultas_prenatal = 'Ignorado/sem informacao')::numeric / NULLIF(COUNT(*), 0) * 100, 2)
FROM silver.sinasc_nascidos_vivos
GROUP BY ano, cod_municipio_residencia;
