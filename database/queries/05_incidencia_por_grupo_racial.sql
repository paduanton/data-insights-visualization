-- Pergunta: a incidencia estimada de sifilis congenita por 1.000 nascidos vivos varia por grupo racial materno?

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
    casos.ano,
    casos.cod_municipio_residencia,
    casos.grupo_racial_mae,
    casos.casos_sc,
    nascidos.nascidos_vivos,
    ROUND(casos.casos_sc::numeric / NULLIF(nascidos.nascidos_vivos, 0) * 1000, 2) AS incidencia_sc_por_1000_nv
FROM casos
JOIN nascidos
  ON nascidos.ano = casos.ano
 AND nascidos.cod_municipio_residencia = casos.cod_municipio_residencia
 AND nascidos.grupo_racial_mae = casos.grupo_racial_mae
WHERE casos.cod_municipio_residencia = '431490'
  AND casos.grupo_racial_mae IN ('Maes negras', 'Maes nao negras')
ORDER BY casos.ano, casos.grupo_racial_mae;
