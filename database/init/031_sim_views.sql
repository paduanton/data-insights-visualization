CREATE SCHEMA IF NOT EXISTS silver;
CREATE SCHEMA IF NOT EXISTS gold;

DROP VIEW IF EXISTS gold.contexto_integrado_municipio_ano;
DROP VIEW IF EXISTS gold.sim_obitos_municipio_ano;
DROP VIEW IF EXISTS silver.sim_obitos;

CREATE VIEW silver.sim_obitos AS
SELECT
    *,
    source_year::integer AS ano,
    LEFT(NULLIF(TRIM(codmunres), ''), 6) AS cod_municipio_residencia,
    LEFT(NULLIF(TRIM(codmunocor), ''), 6) AS cod_municipio_ocorrencia,
    NULLIF(TRIM(causabas), '') AS causa_basica,
    CASE TRIM(racacor)
        WHEN '1' THEN 'Branca'
        WHEN '2' THEN 'Preta'
        WHEN '3' THEN 'Amarela'
        WHEN '4' THEN 'Parda'
        WHEN '5' THEN 'Indigena'
        WHEN '9' THEN 'Ignorada'
        ELSE 'Ignorada'
    END AS raca_cor
FROM bronze.sim_obitos;

CREATE VIEW gold.sim_obitos_municipio_ano AS
SELECT
    ano,
    cod_municipio_residencia,
    COUNT(*) AS obitos_gerais,
    COUNT(*) FILTER (WHERE LEFT(causa_basica, 3) = 'A50') AS obitos_causa_a50,
    COUNT(*) FILTER (WHERE raca_cor = 'Ignorada') AS obitos_raca_ignorada
FROM silver.sim_obitos
WHERE cod_municipio_residencia IS NOT NULL
GROUP BY ano, cod_municipio_residencia;
