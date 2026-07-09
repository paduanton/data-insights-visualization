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
      POSITION('pre' IN LOWER(column_name)) > 0
      OR POSITION('diag' IN LOWER(column_name)) > 0
      OR POSITION('trat' IN LOWER(column_name)) > 0
      OR POSITION('esq' IN LOWER(column_name)) > 0
      OR POSITION('esc' IN LOWER(column_name)) > 0
      OR POSITION('idade' IN LOWER(column_name)) > 0
      OR POSITION('raca' IN LOWER(column_name)) > 0
      OR POSITION('cor' IN LOWER(column_name)) > 0
  )
ORDER BY table_schema, table_name, column_name;
