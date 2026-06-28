# Diretrizes Para Agentes

Este repositório contém um projeto de dados sobre sífilis congênita em Porto Alegre, com pipeline ETL, PostgreSQL, consultas SQL e notebooks analíticos.

## Princípios

- Preserve o foco técnico e analítico do projeto.
- Não adicione linguagem promocional ou referências a obrigações externas ao projeto.
- Mantenha a documentação em português e inglês quando houver resultados, consultas ou mudanças de uso.
- Use commits pequenos, incrementais e em Conventional Commits, com mensagens em português.
- Não remova `docs/references/anteprojeto_sifilis_congenita_poars.pdf`; ele é a referência conceitual preservada.

## Código

- Mantenha o comando `python -m src.etl.load_datasus --strict` compatível.
- Preserve a separação entre camadas `bronze`, `silver` e `gold`.
- Novas consultas devem responder perguntas analíticas claras.
- Notebooks novos devem ficar em `notebooks/analytics/`.

## Documentação

- Atualize `docs/README.pt-BR.md` e `docs/README.en.md` com conteúdo equivalente.
- Resultados visuais devem apontar para imagens em `docs/assets/results/` ou `outputs/images/`, conforme finalidade.
- Ao criar uma análise que dependa de imagem, indique o caminho exato onde a imagem deve ser adicionada.
