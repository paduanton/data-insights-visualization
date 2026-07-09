-- Pergunta: o tratamento materno adequado registrado difere entre maes negras e maes nao negras?

SELECT
    ano,
    cod_municipio_residencia,
    grupo_racial_mae,
    tratamento_materno_adequado,
    casos_sc,
    percentual_no_grupo
FROM gold.tratamento_materno_grupo_racial_municipio_ano
WHERE cod_municipio_residencia = '431490'
  AND grupo_racial_mae IN ('Maes negras', 'Maes nao negras')
ORDER BY ano, grupo_racial_mae, tratamento_materno_adequado;
