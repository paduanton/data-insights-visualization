-- Pergunta: qual e o resumo anual da desigualdade racial na incidencia de sifilis congenita em Porto Alegre?

SELECT
    ano,
    cod_municipio_residencia,
    incidencia_maes_negras,
    incidencia_maes_nao_negras,
    diferenca_absoluta_incidencia,
    razao_incidencia_negras_sobre_nao_negras,
    excesso_relativo_percentual
FROM gold.sintese_desigualdade_racial_municipio_ano
WHERE cod_municipio_residencia = '431490'
ORDER BY ano;
