"""DAG scdp_carga_completa: releitura completa das janelas, a cada 10 dias.

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
    dag_id="scdp_carga_completa",
    description="Releitura completa de todas as janelas desde 2025-01, a cada 10 dias",
    schedule="30 3 */10 * *",
    start_date=datetime(2026, 10, 1),
    catchup=False,
    max_active_runs=1,
    default_args={"owner": "dados", "retries": 1, "retry_delay": timedelta(minutes=15)},
    tags=["scdp", "viagens"],
) as dag:
    BashOperator(
        task_id="carga_completa",
        bash_command=f"{CARGA} --modo completo --desde 2025-01",
        execution_timeout=timedelta(hours=10),
    )
