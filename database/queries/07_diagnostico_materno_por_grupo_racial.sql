-- Pergunta: em que momento o diagnostico materno foi registrado entre os casos por grupo racial?

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
WHERE cod_municipio_residencia = '431490'
  AND grupo_racial_mae IN ('Maes negras', 'Maes nao negras')
GROUP BY ano, cod_municipio_residencia, grupo_racial_mae, momento_diagnostico_materno
ORDER BY ano, grupo_racial_mae, momento_diagnostico_materno;
