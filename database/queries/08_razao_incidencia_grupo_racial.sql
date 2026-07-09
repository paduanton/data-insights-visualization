-- Pergunta: qual e a razao de incidencia estimada entre maes negras e maes nao negras?

SELECT
    ano,
    cod_municipio_residencia,
    incidencia_maes_negras,
    incidencia_maes_nao_negras,
    razao_incidencia_negras_sobre_nao_negras
FROM gold.razao_incidencia_grupo_racial_municipio_ano
WHERE cod_municipio_residencia = '431490'
ORDER BY ano;
