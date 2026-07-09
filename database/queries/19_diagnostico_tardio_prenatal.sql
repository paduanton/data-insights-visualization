-- Pergunta: entre casos com ou sem pre-natal, em que momento o diagnostico materno foi registrado?

SELECT
    grupo_racial_mae,
    realizacao_prenatal,
    momento_diagnostico_materno,
    COUNT(*) AS casos_sc,
    ROUND(
        COUNT(*)::numeric
        / NULLIF(SUM(COUNT(*)) OVER (PARTITION BY grupo_racial_mae, realizacao_prenatal), 0)
        * 100,
        1
    ) AS percentual_no_estrato
FROM silver.sinan_sifilis_congenita
WHERE cod_municipio_residencia = '431490'
  AND grupo_racial_mae IN ('Maes negras', 'Maes nao negras')
GROUP BY grupo_racial_mae, realizacao_prenatal, momento_diagnostico_materno
ORDER BY grupo_racial_mae, realizacao_prenatal, casos_sc DESC;
