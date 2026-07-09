CREATE SCHEMA IF NOT EXISTS bronze;
CREATE SCHEMA IF NOT EXISTS silver;
CREATE SCHEMA IF NOT EXISTS gold;

DROP VIEW IF EXISTS gold.qualidade_registros;
DROP VIEW IF EXISTS gold.razao_incidencia_grupo_racial_municipio_ano;
DROP VIEW IF EXISTS gold.incidencia_grupo_racial_municipio_ano;
DROP VIEW IF EXISTS gold.diagnostico_materno_grupo_racial_municipio_ano;
DROP VIEW IF EXISTS gold.prenatal_grupo_racial_municipio_ano;
DROP VIEW IF EXISTS gold.sinasc_nv_ano_raca;
DROP VIEW IF EXISTS gold.sinan_sc_sem_prenatal_escolaridade;
DROP VIEW IF EXISTS gold.sinan_sc_ano_prenatal;
DROP VIEW IF EXISTS gold.sinan_sc_ano_raca;
DROP VIEW IF EXISTS gold.indicadores_municipio_ano;
DROP VIEW IF EXISTS silver.sinasc_nascidos_vivos;
DROP VIEW IF EXISTS silver.sinan_sifilis_congenita;

CREATE VIEW silver.sinan_sifilis_congenita AS
SELECT
    *,
    source_year::integer AS ano,
    LEFT(NULLIF(TRIM(id_mn_resi), ''), 6) AS cod_municipio_residencia,
    CASE TRIM(ant_raca)
        WHEN '1' THEN 'Branca'
        WHEN '2' THEN 'Preta'
        WHEN '3' THEN 'Amarela'
        WHEN '4' THEN 'Parda'
        WHEN '5' THEN 'Indigena'
        WHEN '9' THEN 'Ignorada'
        ELSE 'Ignorada'
    END AS raca_cor_mae,
    CASE
        WHEN TRIM(ant_raca) IN ('2', '4') THEN 'Maes negras'
        WHEN TRIM(ant_raca) IN ('1', '3', '5') THEN 'Maes nao negras'
        ELSE 'Ignorado/sem informacao'
    END AS grupo_racial_mae,
    CASE TRIM(ant_pre_na)
        WHEN '1' THEN 'Com pre-natal'
        WHEN '2' THEN 'Sem pre-natal'
        WHEN '9' THEN 'Ignorado/sem informacao'
        ELSE 'Ignorado/sem informacao'
    END AS realizacao_prenatal,
    CASE
        WHEN TRIM(escolmae) IN ('02', '03', '04', '05') THEN 'Ate 7 anos de estudo'
        WHEN TRIM(escolmae) IN ('06', '07', '08') THEN '8 anos ou mais de estudo'
        WHEN TRIM(escolmae) IN ('09', '') OR escolmae IS NULL THEN 'Ignorada/sem informacao'
        ELSE 'Ignorada/sem informacao'
    END AS escolaridade_mae,
    CASE TRIM(tra_diag_t)
        WHEN '1' THEN 'Durante o pre-natal'
        WHEN '2' THEN 'No parto/curetagem'
        WHEN '3' THEN 'Apos o parto'
        WHEN '4' THEN 'Nao realizado'
        WHEN '9' THEN 'Ignorado/sem informacao'
        ELSE 'Ignorado/sem informacao'
    END AS momento_diagnostico_materno
FROM bronze.sinan_sifilis_congenita;

CREATE VIEW silver.sinasc_nascidos_vivos AS
SELECT
    *,
    source_year::integer AS ano,
    LEFT(NULLIF(TRIM(codmunres), ''), 6) AS cod_municipio_residencia,
    CASE TRIM(racacormae)
        WHEN '1' THEN 'Branca'
        WHEN '2' THEN 'Preta'
        WHEN '3' THEN 'Amarela'
        WHEN '4' THEN 'Parda'
        WHEN '5' THEN 'Indigena'
        WHEN '9' THEN 'Ignorada'
        ELSE 'Ignorada'
    END AS raca_cor_mae,
    CASE
        WHEN TRIM(racacormae) IN ('2', '4') THEN 'Maes negras'
        WHEN TRIM(racacormae) IN ('1', '3', '5') THEN 'Maes nao negras'
        ELSE 'Ignorado/sem informacao'
    END AS grupo_racial_mae,
    CASE TRIM(consultas)
        WHEN '1' THEN 'Nenhuma'
        WHEN '2' THEN '1 a 3 consultas'
        WHEN '3' THEN '4 a 6 consultas'
        WHEN '4' THEN '7 ou mais consultas'
        WHEN '9' THEN 'Ignorado/sem informacao'
        ELSE 'Ignorado/sem informacao'
    END AS consultas_prenatal,
    CASE
        WHEN TRIM(escmaeagr1) IN ('00', '01', '02', '03', '04') THEN 'Ate 7 anos de estudo'
        WHEN TRIM(escmaeagr1) IN ('05', '06', '07', '08') THEN '8 anos ou mais de estudo'
        WHEN TRIM(escmaeagr1) IN ('09', '10', '11', '12', '') OR escmaeagr1 IS NULL THEN 'Ignorada/sem informacao'
        ELSE 'Ignorada/sem informacao'
    END AS escolaridade_mae
FROM bronze.sinasc_nascidos_vivos;
