SELECT
    ano,
    mes,
    estabelecimentos_distintos,
    tipos_unidade_distintos,
    atividades_distintas
FROM gold.cnes_estabelecimentos_municipio_ano
WHERE cod_municipio = '431490'
ORDER BY ano;
