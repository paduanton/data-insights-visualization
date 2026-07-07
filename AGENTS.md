# Diretrizes Para Agentes

Este repositório contém um projeto de dados sobre sífilis congênita em Porto Alegre, com pipeline ETL, PostgreSQL, consultas SQL e notebooks analíticos.

## Princípios

- Preserve o foco técnico e analítico do projeto.
- Não adicione linguagem promocional ou referências a obrigações externas ao projeto.
- Não remova `docs/references/anteprojeto_sifilis_congenita_poars.pdf`; ele é a referência conceitual preservada.
- Faça mudanças pequenas, incrementais e verificáveis.

## Código

- Mantenha o comando `python -m src.etl.load_datasus --strict` compatível.
- Preserve a separação entre camadas `bronze`, `silver` e `gold`.
- Novas consultas devem responder perguntas analíticas claras.
- Notebooks novos devem ficar em `notebooks/analytics/`.
- Evite mudanças bruscas de arquitetura quando uma refatoração incremental resolver o problema.

## Documentação

- Atualize `docs/README.pt-BR.md` e `docs/README.en.md` com conteúdo equivalente.
- Mantenha `README.md` como entrada curta e bilíngue, apontando para a documentação completa.
- Centralize documentação técnica e de negócio em `docs/README.pt-BR.md` e `docs/README.en.md`.
- Não crie documentação solta fora de `docs/` sem necessidade clara.
- Ao registrar uma nova análise, documente nos dois idiomas:
  - pergunta analítica;
  - fonte ou consulta SQL usada;
  - caminho do notebook;
  - link do Google Colab;
  - caminho da imagem do gráfico;
  - leitura curta do resultado.

## Notebooks E Resultados

- Cada notebook deve responder uma pergunta analítica objetiva.
- Cada notebook documentado deve ter uma linha de referência em `docs/README.pt-BR.md` e `docs/README.en.md`.
- Use este padrão de referência para notebooks:
  - notebook: `notebooks/analytics/<nome>.ipynb`;
  - Colab: `https://colab.research.google.com/github/paduanton/data-insights-visualization/blob/main/notebooks/analytics/<nome>.ipynb`;
  - imagem: `docs/assets/results/<nome-do-resultado>.png`.
- O notebook de visualização principal pode usar imagem em `outputs/images/graphs/` quando o arquivo for resultado direto de geração local.
- Resultados visuais publicados na documentação devem apontar para imagens em `docs/assets/results/` ou `outputs/images/`, conforme finalidade.
- Ao criar uma análise que dependa de imagem, indique o caminho exato onde a imagem deve ser adicionada.

## Commits

- Use Conventional Commits com mensagens em português.
- Prefira escopos quando eles ajudarem a entender a área alterada, por exemplo `docs`, `etl`, `sql`, `notebooks` ou `tests`.
- Faça commits pequenos e coerentes com a evolução do projeto.
- Antes de sugerir ou criar commit, revise `git status` e `git diff` para manter a mensagem alinhada ao conteúdo real.
- Após blocos relevantes de alteração, apresente:
  - mini resumo do que mudou;
  - arquivos alterados, com explicação breve de cada um;
  - sugestão de commit com prefixo Conventional Commits;
  - pergunta objetiva pedindo aprovação antes de executar o commit.
- Execute `git commit` somente quando houver aprovação explícita do usuário.
