-- Pergunta: qual e o perfil de escolaridade e faixa etaria das maes negras nos casos notificados?

WITH casos AS (
    SELECT
        escolaridade_mae,
        CASE
            WHEN idade_mae IS NULL THEN 'Ignorada/sem informacao'
            WHEN idade_mae < 20 THEN 'Ate 19 anos'
            WHEN idade_mae BETWEEN 20 AND 29 THEN '20 a 29 anos'
            WHEN idade_mae BETWEEN 30 AND 39 THEN '30 a 39 anos'
            WHEN idade_mae >= 40 THEN '40 anos ou mais'
            ELSE 'Ignorada/sem informacao'
        END AS faixa_etaria_mae,
        COUNT(*) AS casos_sc
    FROM (
        SELECT
            escolaridade_mae,
            CASE
                WHEN NULLIF(TRIM(ant_idade), '') IS NULL THEN NULL
                WHEN TRIM(ant_idade) !~ '^[0-9]+([.][0-9]+)?$' THEN NULL
                ELSE TRIM(ant_idade)::numeric::integer
            END AS idade_mae
        FROM silver.sinan_sifilis_congenita
        WHERE cod_municipio_residencia = '431490'
          AND grupo_racial_mae = 'Maes negras'
    ) AS base
    GROUP BY escolaridade_mae, faixa_etaria_mae
)
SELECT
    escolaridade_mae,
    faixa_etaria_mae,
    casos_sc,
    ROUND(casos_sc::numeric / SUM(casos_sc) OVER () * 100, 1) AS percentual
FROM casos
ORDER BY escolaridade_mae, faixa_etaria_mae;
