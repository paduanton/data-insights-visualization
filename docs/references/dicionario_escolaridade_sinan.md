# Referencia Operacional: Escolaridade Materna No SINAN/SIFCBR

Este arquivo registra a regra aplicada no projeto para interpretar o campo `ESCOLMAE` dos microdados SINAN/SIFCBR de sifilis congenita.

## Campo

- Fonte: SINAN/SIFCBR.
- Campo bruto: `ESCOLMAE`.
- Campo detalhado no banco: `silver.sinan_sifilis_congenita.escolaridade_mae_detalhada`.
- Campo analitico agrupado no banco: `silver.sinan_sifilis_congenita.escolaridade_mae`.

## Mapeamento Detalhado

| Codigo `ESCOLMAE` | Categoria detalhada usada no projeto |
| --- | --- |
| `00` | Analfabeta |
| `01` | 1a a 4a serie incompleta do EF |
| `02` | 4a serie completa do EF |
| `03` | 5a a 8a serie incompleta do EF |
| `04` | Ensino fundamental completo |
| `05` | Ensino medio incompleto |
| `06` | Ensino medio completo |
| `07` | Educacao superior incompleta |
| `08` | Educacao superior completa |
| `09` | Ignorada |
| `10` | Nao se aplica |
| vazio/nulo/outros | Ignorada |

## Agrupamento Analitico

| Codigos | Grupo analitico |
| --- | --- |
| `00`, `01`, `02`, `03` | Ate 7 anos de estudo |
| `04`, `05`, `06`, `07`, `08` | 8 anos ou mais de estudo |
| `09`, `10`, vazio/nulo/outros | Ignorada/sem informacao |

## Uso Analitico

O agrupamento foi definido para reduzir a fragmentacao de categorias em recortes pequenos, especialmente quando a pergunta cruza casos de sifilis congenita, ausencia de pre-natal, raca/cor materna e municipio.

A leitura correta e:

- `Ate 7 anos de estudo` representa menor escolaridade registrada no SINAN/SIFCBR.
- `8 anos ou mais de estudo` agrega ensino fundamental completo ou escolaridade superior.
- `Ignorada/sem informacao` deve permanecer visivel nos resultados, pois mede qualidade do preenchimento e evita descarte silencioso de registros.

## Implementacao

Esta regra aparece em:

- `database/init/010_silver_views.sql`;
- `src/etl/transform.py`;
- `tests/test_transform.py`;
- `database/queries/12_perfil_variaveis_criticas.sql`.

Ao alterar esta regra, atualize SQL, codigo Python, testes, notebooks e documentacao dos resultados.
