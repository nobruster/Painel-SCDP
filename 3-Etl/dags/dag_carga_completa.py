"""DAG scdp_carga_completa: releitura completa das janelas, nos dias 1, 11 e 21 (a cada ~10 dias).

Se a trava estiver ocupada (codigo 3) a tarefa falha de proposito e o retry tenta de novo: a completa nao pode ser pulada.

Roda o script carga_viagens.py como subprocesso. Variaveis de ambiente do worker (chave da API, PG*, SCHEMA_*)
tem prioridade sobre o .env do projeto.
"""
from datetime import timedelta

import pendulum
from airflow import DAG
from airflow.operators.bash import BashOperator

from scdp.dag_util import comando_carga, comando_reconciliacao

FUSO = "America/Sao_Paulo"

with DAG(
    dag_id="scdp_carga_completa",
    description="Releitura completa de todas as janelas desde 2025-01, nos dias 1, 11 e 21 de cada mes (a cada ~10 dias)",
    schedule="30 3 1,11,21 * *",
    start_date=pendulum.datetime(2026, 10, 1, 3, 30, tz=FUSO),
    catchup=False,
    max_active_runs=1,
    default_args={"owner": "dados", "retries": 1, "retry_delay": timedelta(minutes=15)},
    tags=["scdp", "viagens"],
) as dag:
    carga = BashOperator(
        task_id="carga_completa",
        bash_command=comando_carga("--modo", "completo", "--desde", "2025-01"),
        execution_timeout=timedelta(hours=10),
    )
    reconciliar = BashOperator(
        task_id="reconciliar",
        bash_command=comando_reconciliacao(),
        retries=0,
        execution_timeout=timedelta(minutes=10),
    )
    carga >> reconciliar
