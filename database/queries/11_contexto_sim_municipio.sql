SELECT
    ano,
    obitos_gerais,
    obitos_causa_a50,
    obitos_raca_ignorada
FROM gold.sim_obitos_municipio_ano
WHERE cod_municipio_residencia = '431490'
ORDER BY ano;
