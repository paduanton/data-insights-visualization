-- Pergunta: a incidencia estimada de sifilis congenita por 1.000 nascidos vivos varia por grupo racial materno?

SELECT
    ano,
    cod_municipio_residencia,
    grupo_racial_mae,
    casos_sc,
    nascidos_vivos,
    incidencia_sc_por_1000_nv
FROM gold.incidencia_grupo_racial_municipio_ano
WHERE cod_municipio_residencia = '431490'
  AND grupo_racial_mae IN ('Maes negras', 'Maes nao negras')
ORDER BY ano, grupo_racial_mae;
