SELECT
    ano,
    cod_municipio_residencia,
    casos_sc,
    nascidos_vivos,
    incidencia_sc_por_1000_nv
FROM gold.indicadores_municipio_ano
WHERE cod_municipio_residencia = '431490'
ORDER BY ano;
