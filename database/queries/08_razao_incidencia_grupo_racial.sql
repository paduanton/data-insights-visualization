-- Pergunta: qual e a razao de incidencia estimada entre maes negras e maes nao negras?

WITH incidencia AS (
    SELECT
        casos.ano,
        casos.cod_municipio_residencia,
        casos.grupo_racial_mae,
        casos.casos_sc,
        nascidos.nascidos_vivos,
        casos.casos_sc::numeric / NULLIF(nascidos.nascidos_vivos, 0) * 1000 AS incidencia_sc_por_1000_nv
    FROM (
        SELECT
            ano,
            cod_municipio_residencia,
            grupo_racial_mae,
            SUM(casos_sc) AS casos_sc
        FROM gold.sinan_sc_ano_raca
        GROUP BY ano, cod_municipio_residencia, grupo_racial_mae
    ) AS casos
    JOIN (
        SELECT
            ano,
            cod_municipio_residencia,
            grupo_racial_mae,
            SUM(nascidos_vivos) AS nascidos_vivos
        FROM gold.sinasc_nv_ano_raca
        GROUP BY ano, cod_municipio_residencia, grupo_racial_mae
    ) AS nascidos
      ON nascidos.ano = casos.ano
     AND nascidos.cod_municipio_residencia = casos.cod_municipio_residencia
     AND nascidos.grupo_racial_mae = casos.grupo_racial_mae
    WHERE casos.cod_municipio_residencia = '431490'
      AND casos.grupo_racial_mae IN ('Maes negras', 'Maes nao negras')
)
SELECT
    negras.ano,
    negras.cod_municipio_residencia,
    ROUND(negras.incidencia_sc_por_1000_nv, 2) AS incidencia_maes_negras,
    ROUND(nao_negras.incidencia_sc_por_1000_nv, 2) AS incidencia_maes_nao_negras,
    ROUND(
        negras.incidencia_sc_por_1000_nv / NULLIF(nao_negras.incidencia_sc_por_1000_nv, 0),
        2
    ) AS razao_incidencia_negras_sobre_nao_negras
FROM incidencia AS negras
JOIN incidencia AS nao_negras
  ON nao_negras.ano = negras.ano
 AND nao_negras.cod_municipio_residencia = negras.cod_municipio_residencia
WHERE negras.grupo_racial_mae = 'Maes negras'
  AND nao_negras.grupo_racial_mae = 'Maes nao negras'
ORDER BY negras.ano;
