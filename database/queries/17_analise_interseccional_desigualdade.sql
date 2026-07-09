-- Pergunta: marcadores combinados de vulnerabilidade aparecem de forma desigual entre grupos raciais?
-- Analise descritiva, sem inferencia causal e sem pareamento individual.

WITH casos AS (
    SELECT
        ano,
        grupo_racial_mae,
        escolaridade_mae,
        realizacao_prenatal,
        momento_diagnostico_materno,
        tratamento_materno_adequado,
        CASE
            WHEN escolaridade_mae IN ('Ate 7 anos de estudo', 'Ignorada/sem informacao')
             AND (
                    realizacao_prenatal IN ('Sem pre-natal', 'Ignorado/sem informacao')
                 OR momento_diagnostico_materno IN ('No parto/curetagem', 'Apos o parto', 'Nao realizado')
                 OR tratamento_materno_adequado IN ('Inadequado', 'Ignorado/sem informacao')
             )
            THEN 'Maior vulnerabilidade registrada'
            ELSE 'Demais casos'
        END AS marcador_vulnerabilidade,
        COUNT(*) AS casos_sc
    FROM silver.sinan_sifilis_congenita
    WHERE cod_municipio_residencia = '431490'
      AND grupo_racial_mae IN ('Maes negras', 'Maes nao negras')
    GROUP BY
        ano,
        grupo_racial_mae,
        escolaridade_mae,
        realizacao_prenatal,
        momento_diagnostico_materno,
        tratamento_materno_adequado,
        marcador_vulnerabilidade
),
resumo AS (
    SELECT
        grupo_racial_mae,
        marcador_vulnerabilidade,
        SUM(casos_sc) AS casos_sc
    FROM casos
    GROUP BY grupo_racial_mae, marcador_vulnerabilidade
)
SELECT
    grupo_racial_mae,
    marcador_vulnerabilidade,
    casos_sc,
    ROUND(
        casos_sc::numeric
        / NULLIF(SUM(casos_sc) OVER (PARTITION BY grupo_racial_mae), 0)
        * 100,
        1
    ) AS percentual_no_grupo
FROM resumo
ORDER BY grupo_racial_mae, marcador_vulnerabilidade;
