-- Pergunta: como a realizacao de pre-natal se distribui entre os casos de sifilis congenita por grupo racial materno?

SELECT
    ano,
    cod_municipio_residencia,
    grupo_racial_mae,
    realizacao_prenatal,
    casos_sc,
    ROUND(
        casos_sc::numeric / NULLIF(SUM(casos_sc) OVER (PARTITION BY ano, cod_municipio_residencia, grupo_racial_mae), 0) * 100,
        1
    ) AS percentual_no_grupo
FROM gold.sinan_sc_ano_prenatal
WHERE cod_municipio_residencia = '431490'
  AND grupo_racial_mae IN ('Maes negras', 'Maes nao negras')
ORDER BY ano, grupo_racial_mae, realizacao_prenatal;
