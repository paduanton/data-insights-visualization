CREATE SCHEMA IF NOT EXISTS gold;

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
