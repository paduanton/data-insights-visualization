# Fontes de dados do anteprojeto

## Fontes centrais

- DATASUS Transferência de Arquivos: fonte primária dos microdados `.dbc`.
- SINAN/SIFCBR: casos de sífilis congênita e trajetória assistencial.
- SINASC: nascidos vivos, perfil materno e denominador para incidência.

## Fontes complementares

- DATASUS TabNet: validação agregada e séries históricas em CSV.
- IBGE Localidades: padronização territorial.
- IBGE SIDRA/Censo/PNAD: contexto socioeconômico agregado.
- CNES: contexto de oferta assistencial.
- SIM: mortalidade e desfechos graves em agregações.
- Base dos Dados: fonte auxiliar para acelerar acesso a dados públicos tratados.

## Critério técnico

O banco deve priorizar análises agregadas por município, ano e estratos. As bases públicas não serão usadas para ligação individual entre SINAN e SINASC.
