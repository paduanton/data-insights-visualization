-- Pergunta: em que momento o diagnostico materno foi registrado entre os casos por grupo racial?

SELECT
    ano,
    cod_municipio_residencia,
    grupo_racial_mae,
    momento_diagnostico_materno,
    casos_sc,
    percentual_no_grupo
FROM gold.diagnostico_materno_grupo_racial_municipio_ano
WHERE cod_municipio_residencia = '431490'
  AND grupo_racial_mae IN ('Maes negras', 'Maes nao negras')
ORDER BY ano, grupo_racial_mae, momento_diagnostico_materno;
