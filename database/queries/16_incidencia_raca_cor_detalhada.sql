-- Pergunta: como a incidencia estimada varia por categoria detalhada de raca/cor materna?
-- Observacao: esta analise e complementar. Categorias com baixo denominador devem ser interpretadas com cautela.

WITH casos AS (
    SELECT
        ano,
        cod_municipio_residencia,
        raca_cor_mae,
        COUNT(*) AS casos_sc
    FROM silver.sinan_sifilis_congenita
    GROUP BY ano, cod_municipio_residencia, raca_cor_mae
),
nascidos AS (
    SELECT
        ano,
        cod_municipio_residencia,
        raca_cor_mae,
        COUNT(*) AS nascidos_vivos
    FROM silver.sinasc_nascidos_vivos
    GROUP BY ano, cod_municipio_residencia, raca_cor_mae
)
SELECT
    COALESCE(casos.ano, nascidos.ano) AS ano,
    COALESCE(casos.cod_municipio_residencia, nascidos.cod_municipio_residencia) AS cod_municipio_residencia,
    COALESCE(casos.raca_cor_mae, nascidos.raca_cor_mae) AS raca_cor_mae,
    COALESCE(casos.casos_sc, 0) AS casos_sc,
    COALESCE(nascidos.nascidos_vivos, 0) AS nascidos_vivos,
    ROUND(
        COALESCE(casos.casos_sc, 0)::numeric
        / NULLIF(nascidos.nascidos_vivos, 0)
        * 1000,
        2
    ) AS incidencia_sc_por_1000_nv,
    CASE
        WHEN COALESCE(nascidos.nascidos_vivos, 0) < 30 THEN 'baixo denominador: interpretar com cautela'
        ELSE 'ok'
    END AS alerta_interpretacao
FROM casos
FULL OUTER JOIN nascidos
    ON nascidos.ano = casos.ano
   AND nascidos.cod_municipio_residencia = casos.cod_municipio_residencia
   AND nascidos.raca_cor_mae = casos.raca_cor_mae
WHERE COALESCE(casos.cod_municipio_residencia, nascidos.cod_municipio_residencia) = '431490'
ORDER BY ano, raca_cor_mae;
