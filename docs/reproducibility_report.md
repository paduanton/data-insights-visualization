# Relatório De Reprodutibilidade

Este relatório registra os comandos de validação executados durante o refinamento final do projeto.

## Ambiente

- Projeto: `data-insights-visualization`
- Recorte principal: Porto Alegre, RS, Brasil
- Período consolidado: `2015-2024`
- Banco: PostgreSQL via Docker Compose
- Linguagem: Python

## Comandos Executados

| Comando | Status | Observações |
| --- | --- | --- |
| `docker compose config` | OK | Configuração do PostgreSQL e pgAdmin validada. Houve aviso de permissão no arquivo global `~/.docker/config.json`, sem bloquear a validação do compose. |
| `.\\.venv-codex\\Scripts\\python.exe -m src.visualization.final_report` | OK | Gerou as imagens finais em `outputs/images/final_report/`. |
| `.\\.venv-codex\\Scripts\\python.exe -m src.notebooks.execute_notebooks notebooks/11_analise_interseccional_desigualdade.ipynb notebooks/12_relatorio_final_consolidado.ipynb` | OK | Executou os notebooks finais e regenerou imagens finais. |
| `.\\.venv-codex\\Scripts\\python.exe -m pytest` | OK | `34 passed`, com avisos deprecados do Matplotlib/PyParsing sem falha de teste. |
| `.\\.venv-codex\\Scripts\\python.exe -c \"import json, pathlib; ...\"` | OK | `14` notebooks com JSON válido. |
| `.\\.venv-codex\\Scripts\\python.exe -m src.notebooks.execute_notebooks` | OK | Executou todos os notebooks registrados no executor padrão e regenerou imagens derivadas. |
| `git diff --check` | OK | Sem erros de whitespace. Houve apenas aviso de CRLF em arquivos de texto. |

## Correções Aplicadas

- A documentação passou a citar os dois gráficos do notebook `07_diagnostico_tratamento_cuidado.ipynb`.
- Foram criadas consultas SQL para raça/cor detalhada, análise interseccional, perfil de mães negras e diagnóstico por pré-natal.
- Foram criados os notebooks finais `11_analise_interseccional_desigualdade.ipynb` e `12_relatorio_final_consolidado.ipynb`.
- Foi criado o gerador `src.visualization.final_report` para exportar imagens finais reprodutíveis.
- A visualização de raça/cor detalhada foi ajustada para não distorcer a escala com categorias de denominador instável.
- O perfil por faixa etária passou a usar `ANT_IDADE` convertido de texto decimal para número.

## Pendências

- Revisar visualmente os PNGs finais antes do commit, quando desejado.
- Confirmar `git status` limpo após commit aprovado.
- O comando `git status` emite aviso de permissão no ignore global `C:\\Users\\AntonioPádua\\.config\\git\\ignore`; isso não altera os arquivos do repositório.
