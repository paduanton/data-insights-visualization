SELECT 'bronze.sinan_sifilis_congenita' AS tabela, COUNT(*) AS linhas
FROM bronze.sinan_sifilis_congenita
UNION ALL
SELECT 'bronze.sinasc_nascidos_vivos', COUNT(*)
FROM bronze.sinasc_nascidos_vivos;

SELECT 'SINAN Porto Alegre' AS recorte, COUNT(*) AS linhas
FROM silver.sinan_sifilis_congenita
WHERE ano = 2024 AND cod_municipio_residencia = '431490'
UNION ALL
SELECT 'SINASC Porto Alegre', COUNT(*)
FROM silver.sinasc_nascidos_vivos
WHERE ano = 2024 AND cod_municipio_residencia = '431490';
