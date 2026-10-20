"""Monta o comando que as DAGs executam (sem importar o Airflow, para poder ser testado).

O caminho do projeto e o Python do worker sao resolvidos pelo proprio bash quando a tarefa roda
(variaveis PAINEL_SCDP_HOME e PAINEL_SCDP_PYTHON do worker), e nao quando o scheduler le o arquivo da DAG.
"""
from __future__ import annotations

import shlex

from .codigos import CODIGO_OCUPADO  # noqa: F401  (reexportado para as DAGs)

RAIZ_PADRAO = "/opt/repos/Painel-SCDP"
PYTHON_PADRAO = "/opt/airflow/venv/bin/python"


def comando_carga(*argumentos: str) -> str:
    python = '"${PAINEL_SCDP_PYTHON:-%s}"' % PYTHON_PADRAO
    script = '"${PAINEL_SCDP_HOME:-%s}/3-Etl/dags/carga_viagens.py"' % RAIZ_PADRAO
    return " ".join([python, "-I", script, *[shlex.quote(a) for a in argumentos]])
