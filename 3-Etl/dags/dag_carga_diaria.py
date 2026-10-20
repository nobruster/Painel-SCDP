"""DAG scdp_carga_diaria: carga incremental diaria das viagens do SCDP.

Roda o script carga_viagens.py como subprocesso. Variaveis de ambiente do worker (chave da API, PG*, SCHEMA_*)
tem prioridade sobre o .env do projeto.
"""
from datetime import timedelta

import pendulum
from airflow import DAG
from airflow.operators.bash import BashOperator

from scdp.dag_util import CODIGO_OCUPADO, comando_carga, comando_reconciliacao

FUSO = "America/Sao_Paulo"

with DAG(
    dag_id="scdp_carga_diaria",
    description="Carga incremental diaria das viagens (janelas dos ultimos 3 meses + pendentes)",
    schedule="0 2 * * *",
    start_date=pendulum.datetime(2026, 10, 1, tz=FUSO),
    catchup=False,
    max_active_runs=1,
    default_args={"owner": "dados", "retries": 1, "retry_delay": timedelta(minutes=15)},
    tags=["scdp", "viagens"],
) as dag:
    carga = BashOperator(
        task_id="carga_diaria",
        bash_command=comando_carga("--modo", "diario"),
        skip_on_exit_code=CODIGO_OCUPADO,
        execution_timeout=timedelta(hours=5),
    )
    reconciliar = BashOperator(
        task_id="reconciliar",
        bash_command=comando_reconciliacao(),
        retries=0,
        execution_timeout=timedelta(minutes=10),
    )
    carga >> reconciliar
