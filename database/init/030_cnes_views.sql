CREATE SCHEMA IF NOT EXISTS silver;
CREATE SCHEMA IF NOT EXISTS gold;

DROP VIEW IF EXISTS gold.cnes_estabelecimentos_municipio_ano;
DROP VIEW IF EXISTS silver.cnes_estabelecimentos;

CREATE VIEW silver.cnes_estabelecimentos AS
SELECT
    *,
    source_year::integer AS ano,
    NULLIF(TRIM(source_month), '')::integer AS mes,
    LEFT(NULLIF(TRIM(codufmun), ''), 6) AS cod_municipio,
    NULLIF(TRIM(cnes), '') AS cnes_id,
    NULLIF(TRIM(tp_unid), '') AS tipo_unidade_codigo,
    NULLIF(TRIM(atividad), '') AS atividade_codigo
FROM bronze.cnes_estabelecimentos;

CREATE VIEW gold.cnes_estabelecimentos_municipio_ano AS
SELECT
    ano,
    mes,
    cod_municipio,
    COUNT(*) AS registros_cnes,
    COUNT(DISTINCT cnes_id) AS estabelecimentos_distintos,
    COUNT(DISTINCT tipo_unidade_codigo) AS tipos_unidade_distintos,
    COUNT(DISTINCT atividade_codigo) AS atividades_distintas
FROM silver.cnes_estabelecimentos
WHERE cod_municipio IS NOT NULL
GROUP BY ano, mes, cod_municipio;
