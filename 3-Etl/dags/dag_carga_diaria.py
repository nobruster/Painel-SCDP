"""DAG scdp_carga_diaria: carga incremental diaria das viagens do SCDP.

Roda o script carga_viagens.py como subprocesso (ele le o .env e as variaveis
de ambiente ao ser importado, entao nao deve ser importado pelo Airflow).
Variaveis de ambiente do Airflow tem prioridade sobre o .env do projeto.
"""
import os
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator

RAIZ = os.environ.get("PAINEL_SCDP_HOME", "/opt/repos/Painel-SCDP")
PYTHON = os.environ.get("PAINEL_SCDP_PYTHON", "/opt/airflow/venv/bin/python")
CARGA = f"{PYTHON} -I {RAIZ}/3-Etl/dags/carga_viagens.py"

with DAG(
    dag_id="scdp_carga_diaria",
    description="Carga incremental diaria das viagens (janelas dos ultimos 3 meses + pendentes)",
    schedule="0 2 * * *",
    start_date=datetime(2026, 10, 1),
    catchup=False,
    max_active_runs=1,
    default_args={"owner": "dados", "retries": 1, "retry_delay": timedelta(minutes=15)},
    tags=["scdp", "viagens"],
) as dag:
    BashOperator(
        task_id="carga_diaria",
        bash_command=f"{CARGA} --modo diario",
        execution_timeout=timedelta(hours=5),
    )
