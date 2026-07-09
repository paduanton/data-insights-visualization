-- Pergunta: quais codigos brutos e categorias aplicadas sustentam as variaveis criticas do schema analitico?

WITH distribuicoes AS (
    SELECT
        'SINAN/SIFCBR' AS base,
        'raca_cor_mae' AS variavel,
        COALESCE(NULLIF(TRIM(ant_raca), ''), '<vazio>') AS codigo_bruto,
        grupo_racial_mae AS categoria_analitica,
        COUNT(*) AS registros
    FROM silver.sinan_sifilis_congenita
    GROUP BY COALESCE(NULLIF(TRIM(ant_raca), ''), '<vazio>'), grupo_racial_mae

    UNION ALL

    SELECT
        'SINAN/SIFCBR',
        'pre_natal',
        COALESCE(NULLIF(TRIM(ant_pre_na), ''), '<vazio>'),
        realizacao_prenatal,
        COUNT(*)
    FROM silver.sinan_sifilis_congenita
    GROUP BY COALESCE(NULLIF(TRIM(ant_pre_na), ''), '<vazio>'), realizacao_prenatal

    UNION ALL

    SELECT
        'SINAN/SIFCBR',
        'escolaridade_mae',
        COALESCE(NULLIF(TRIM(escolmae), ''), '<vazio>'),
        escolaridade_mae,
        COUNT(*)
    FROM silver.sinan_sifilis_congenita
    GROUP BY COALESCE(NULLIF(TRIM(escolmae), ''), '<vazio>'), escolaridade_mae

    UNION ALL

    SELECT
        'SINAN/SIFCBR',
        'escolaridade_mae_detalhada',
        COALESCE(NULLIF(TRIM(escolmae), ''), '<vazio>'),
        escolaridade_mae_detalhada,
        COUNT(*)
    FROM silver.sinan_sifilis_congenita
    GROUP BY COALESCE(NULLIF(TRIM(escolmae), ''), '<vazio>'), escolaridade_mae_detalhada

    UNION ALL

    SELECT
        'SINAN/SIFCBR',
        'momento_diagnostico_materno',
        COALESCE(NULLIF(TRIM(tra_diag_t), ''), '<vazio>'),
        momento_diagnostico_materno,
        COUNT(*)
    FROM silver.sinan_sifilis_congenita
    GROUP BY COALESCE(NULLIF(TRIM(tra_diag_t), ''), '<vazio>'), momento_diagnostico_materno

    UNION ALL

    SELECT
        'SINASC',
        'raca_cor_mae',
        COALESCE(NULLIF(TRIM(racacormae), ''), '<vazio>'),
        grupo_racial_mae,
        COUNT(*)
    FROM silver.sinasc_nascidos_vivos
    GROUP BY COALESCE(NULLIF(TRIM(racacormae), ''), '<vazio>'), grupo_racial_mae

    UNION ALL

    SELECT
        'SINASC',
        'consultas_prenatal',
        COALESCE(NULLIF(TRIM(consultas), ''), '<vazio>'),
        consultas_prenatal,
        COUNT(*)
    FROM silver.sinasc_nascidos_vivos
    GROUP BY COALESCE(NULLIF(TRIM(consultas), ''), '<vazio>'), consultas_prenatal

    UNION ALL

    SELECT
        'SINASC',
        'escolaridade_mae',
        COALESCE(NULLIF(TRIM(escmaeagr1), ''), '<vazio>'),
        escolaridade_mae,
        COUNT(*)
    FROM silver.sinasc_nascidos_vivos
    GROUP BY COALESCE(NULLIF(TRIM(escmaeagr1), ''), '<vazio>'), escolaridade_mae

    UNION ALL

    SELECT
        'SIM/DO',
        'raca_cor',
        COALESCE(NULLIF(TRIM(racacor), ''), '<vazio>'),
        raca_cor,
        COUNT(*)
    FROM silver.sim_obitos
    GROUP BY COALESCE(NULLIF(TRIM(racacor), ''), '<vazio>'), raca_cor
)
SELECT
    base,
    variavel,
    codigo_bruto,
    categoria_analitica,
    registros,
    ROUND(registros::numeric / SUM(registros) OVER (PARTITION BY base, variavel) * 100, 2) AS percentual
FROM distribuicoes
ORDER BY base, variavel, codigo_bruto, categoria_analitica;
