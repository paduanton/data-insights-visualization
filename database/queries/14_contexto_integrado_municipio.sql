-- Pergunta: como a incidencia de sifilis congenita se posiciona junto ao contexto populacional, assistencial e de mortalidade em Porto Alegre?

SELECT
    ano,
    cod_municipio,
    casos_sc,
    nascidos_vivos,
    incidencia_sc_por_1000_nv,
    populacao_residente,
    casos_sc_por_100000_habitantes,
    estabelecimentos_distintos,
    tipos_unidade_distintos,
    obitos_gerais,
    obitos_causa_a50,
    obitos_raca_ignorada
FROM gold.contexto_integrado_municipio_ano
WHERE cod_municipio = '431490'
ORDER BY ano;
