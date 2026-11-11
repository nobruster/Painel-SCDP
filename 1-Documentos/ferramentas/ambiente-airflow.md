# Ambiente de execução do Airflow

Estado atual conforme `3-Etl/dags/scdp/dag_util.py`, as DAGs e o PRD. Nenhum valor de segredo é registrado aqui.

## Versão

Airflow 2.10. DAGs: `scdp_carga_diaria` (`dag_carga_diaria.py`, cron `0 2 * * *`) e `scdp_carga_completa` (`dag_carga_completa.py`, cron `30 3 1,11,21 * *`). Ambas com `max_active_runs=1`, `retries=1` e espera de 15 minutos entre tentativas; a tarefa `reconciliar` e as de validação têm `retries=0`.

## Caminho

O comando é montado por `comando_carga` em `dag_util.py` e resolvido pelo bash do worker na hora da execução (não quando o scheduler lê a DAG):

- `PAINEL_SCDP_HOME`: raiz do repositório no worker. Padrão: `/opt/repos/Painel-SCDP`. O script executado é `$PAINEL_SCDP_HOME/3-Etl/dags/carga_viagens.py`; a reconciliação e a validação das janelas usam `2-Scripts/` na mesma raiz.
- Como o repositório chega ao worker (clone, volume montado, imagem): **pergunta aberta**, depende de quem administra o Airflow do órgão.

## Python

- `PAINEL_SCDP_PYTHON`: interpretador do worker. Padrão: `/opt/airflow/venv/bin/python`. É sempre chamado com `-I` (modo isolado).
- O CI usa Python 3.11. A versão exata do Python do worker e as dependências instaladas no venv: **pergunta aberta**.

## .airflowignore

`3-Etl/dags/.airflowignore` ignora `scdp/` e `sql/`, para o Airflow não tentar ler o pacote e o DDL como DAGs. Só `dag_carga_diaria.py` e `dag_carga_completa.py` (e `carga_viagens.py`, sem DAG) ficam visíveis.

## Segredos

- Hoje: o `.env` do projeto no servidor (`PORTAL_TRANSPARENCIA_*`, `CODIGO_ORGAO`, `PG*`, `SCHEMA_*`) ou variáveis de ambiente do worker, que têm prioridade sobre o arquivo. O `.env` não vai para o git; o modelo é `.env.example`.
- `ALERTA_WEBHOOK_URL` (ADR 0003) também é segredo e vem do ambiente do worker.
- Connections e Variables do Airflow ainda não são usadas: **pendente**. Quando forem, a chave da API, a senha do banco e o webhook migram para lá.

## Pool

As DAGs não usam pool (nenhum `pool=` no código). A proteção contra execução simultânea é `max_active_runs=1` em cada DAG e a trava de banco (advisory lock) no código; esta última impede a diária e a completa de rodarem juntas (código de saída 3, tarefa *skipped* na diária). Um pool para limitar chamadas à API entre DAGs: **pergunta aberta**; o limite de requisições (50% de 400/min) é controlado dentro do próprio código.

## Fuso

`America/Sao_Paulo`, fixado nas DAGs porque a interface do Airflow mostra UTC. Os horários (02:00 diária; 03:30 completa nos dias 1, 11 e 21) caem na faixa de 700 req/min da API (0:00 às 5:59).

## Comandos de teste

Rodar da raiz do projeto. Os testes de banco usam schemas `zz_teste_*` e `TEST_DATABASE_URL`.

```
python -I -m pytest tests -q
python -I 3-Etl/dags/carga_viagens.py --modo diario
python -I 3-Etl/dags/carga_viagens.py --modo completo --desde 2026-01
```

No Airflow, testar uma tarefa sem agendar: `airflow tasks test scdp_carga_diaria <tarefa> <data>`. Conferir o carregamento das DAGs: `airflow dags list-import-errors`.
