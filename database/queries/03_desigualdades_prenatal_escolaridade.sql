SELECT
    ano,
    cod_municipio_residencia,
    grupo_racial_mae,
    escolaridade_mae,
    casos_sc,
    ROUND(
        casos_sc::numeric / NULLIF(SUM(casos_sc) OVER (PARTITION BY ano, cod_municipio_residencia, grupo_racial_mae), 0) * 100,
        1
    ) AS percentual_no_grupo
FROM gold.sinan_sc_sem_prenatal_escolaridade
WHERE ano = 2024
  AND cod_municipio_residencia = '431490'
  AND grupo_racial_mae IN ('Maes negras', 'Maes nao negras')
ORDER BY ano, grupo_racial_mae, escolaridade_mae;
