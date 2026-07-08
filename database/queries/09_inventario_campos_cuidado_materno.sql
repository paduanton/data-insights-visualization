-- Pergunta: quais campos brutos podem sustentar analises de pre-natal, diagnostico e tratamento materno?

SELECT
    table_schema,
    table_name,
    column_name,
    data_type
FROM information_schema.columns
WHERE table_schema IN ('bronze', 'silver')
  AND table_name IN ('sinan_sifilis_congenita', 'sinasc_nascidos_vivos')
  AND (
      column_name ILIKE '%pre%'
      OR column_name ILIKE '%diag%'
      OR column_name ILIKE '%trat%'
      OR column_name ILIKE '%esq%'
      OR column_name ILIKE '%esc%'
      OR column_name ILIKE '%idade%'
      OR column_name ILIKE '%raca%'
      OR column_name ILIKE '%cor%'
  )
ORDER BY table_schema, table_name, column_name;
