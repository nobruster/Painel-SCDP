"""DAG completa: validar_janelas vem depois de reconciliar, sem retry, com o comando montado em scdp/dag_util.py."""
from pathlib import Path

from scdp.dag_util import comando_validar_janelas

DAGS = Path(__file__).resolve().parent.parent / "3-Etl" / "dags"


def test_validar_janelas_vem_depois_de_reconciliar_e_sem_retry():
    texto = (DAGS / "dag_carga_completa.py").read_text(encoding="utf-8")
    assert 'task_id="validar_janelas"' in texto and "comando_validar_janelas()" in texto
    assert "carga >> reconciliar >> validar_janelas" in texto
    bloco = texto[texto.index('task_id="validar_janelas"'):]
    assert "retries=0" in bloco


def test_gate_nao_esta_na_dag_diaria():
    assert "validar_janelas" not in (DAGS / "dag_carga_diaria.py").read_text(encoding="utf-8")


def test_comando_usa_as_variaveis_do_worker_e_o_script_que_existe():
    cmd = comando_validar_janelas()
    assert "${PAINEL_SCDP_PYTHON:-/opt/airflow/venv/bin/python}" in cmd and " -I " in cmd
    assert "${PAINEL_SCDP_HOME:-/opt/repos/Painel-SCDP}/2-Scripts/validar_carga_completa.py" in cmd
    assert "{{" not in cmd and "{%" not in cmd
    assert (DAGS.parent.parent / "2-Scripts" / "validar_carga_completa.py").is_file()
