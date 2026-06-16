SELECT
    base,
    ano,
    cod_municipio_residencia,
    variavel,
    ignorados,
    total,
    percentual_ignorado
FROM gold.qualidade_registros
WHERE cod_municipio_residencia = '431490'
ORDER BY base, ano, variavel;
