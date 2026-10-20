"""Testes sem banco: linha de comando, descricao segura de erros, comando e arquivos de DAG."""
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import psycopg2
import pytest

from scdp import cli
from scdp.config import ErroConfiguracao
from scdp.dag_util import comando_carga
from scdp.erros import descrever

DAGS = Path(__file__).resolve().parent.parent / "3-Etl" / "dags"


def test_desde_invalido_sai_com_codigo_2():
    for ruim in ("2025/01", "janeiro", "2010-01", "2099-01"):
        with pytest.raises(SystemExit) as e:
            cli.criar_parser().parse_args(["--desde", ruim])
        assert e.value.code == 2


def test_desde_valido():
    assert cli.criar_parser().parse_args(["--desde", "2025-03"]).desde.isoformat() == "2025-03-01"


def test_configuracao_ausente_sai_com_codigo_2(monkeypatch):
    def falta(*a, **k):
        raise ErroConfiguracao("faltam variaveis")

    monkeypatch.setattr(cli.Config, "do_ambiente", classmethod(falta))
    assert cli.main(["--modo", "diario"]) == 2


def test_sigterm_devolve_143_e_fecha_a_conexao(monkeypatch, cfg):
    fechada = []

    class Conexao:
        def cursor(self):
            return object()

        def close(self):
            fechada.append(True)

    class PipelineQueRecebeSigterm:
        def __init__(self, *a, **k):
            pass

        def executar(self, *a, **k):
            raise KeyboardInterrupt("sinal 15")

    monkeypatch.setattr(cli.Config, "do_ambiente", classmethod(lambda cls, env_file=None: cfg))
    monkeypatch.setattr(cli.carga, "conectar", lambda c: Conexao())
    monkeypatch.setattr(cli, "Pipeline", PipelineQueRecebeSigterm)
    assert cli.main(["--modo", "diario"]) == 143
    assert fechada == [True]


def _erro_pg(principal, pgcode="22P02"):
    class ErroPg(psycopg2.Error):
        diag = SimpleNamespace(message_primary=principal)

    e = ErroPg("texto do erro")
    e.__class__.pgcode = pgcode
    return e


def test_descrever_erro_do_postgres_nao_inclui_o_detail(cfg):
    erro = psycopg2.Error('violacao de chave\nDETAIL:  Failing row contains (1, FULANO DE TAL, ***.123.456-**)')
    texto = descrever(cfg, erro)
    assert "FULANO" not in texto and "violacao de chave" in texto


def test_descrever_erro_do_postgres_nao_inclui_o_valor_ofensivo(cfg):
    texto = descrever(cfg, _erro_pg('invalid input syntax for type bigint: "FULANO DE TAL"'))
    assert "FULANO" not in texto
    assert "invalid input syntax for type bigint" in texto and "22P02" in texto
    assert "FULANO" not in descrever(cfg, _erro_pg('duplicate key value violates unique constraint "pk_FULANO"'))


def test_descrever_mascara_segredos(cfg):
    assert "chave-de-teste" not in descrever(cfg, RuntimeError("falha com chave-de-teste"))


def test_comando_da_dag_resolve_o_ambiente_no_bash_e_escapa_argumentos():
    cmd = comando_carga("--modo", "completo", "--desde", "2025-01; rm -rf /")
    assert "${PAINEL_SCDP_PYTHON:-/opt/airflow/venv/bin/python}" in cmd
    assert "${PAINEL_SCDP_HOME:-/opt/repos/Painel-SCDP}/3-Etl/dags/carga_viagens.py" in cmd
    assert "'2025-01; rm -rf /'" in cmd
    assert "{{" not in cmd and "{%" not in cmd, "nao pode ser lido como Jinja"


@pytest.mark.skipif(shutil.which("bash") is None or sys.platform == "win32", reason="precisa de bash POSIX (roda no CI)")
def test_comando_da_dag_funciona_com_caminho_com_espaco(tmp_path):
    projeto = tmp_path / "meu projeto"
    (projeto / "3-Etl" / "dags").mkdir(parents=True)
    script = projeto / "3-Etl" / "dags" / "carga_viagens.py"
    script.write_text("", encoding="utf-8")
    cmd = comando_carga("--modo", "diario")
    env = {"PAINEL_SCDP_PYTHON": "echo", "PAINEL_SCDP_HOME": str(projeto), "PATH": os.environ.get("PATH", "")}
    saida = subprocess.run(["bash", "-c", cmd], env=env, capture_output=True, text=True).stdout
    assert str(projeto) in saida
    assert saida.strip().endswith("--modo diario")


def test_dag_ids_sao_unicos_entre_os_arquivos():
    ids = []
    for arquivo in sorted(DAGS.glob("dag_*.py")):
        ids += re.findall(r'dag_id\s*=\s*"([^"]+)"', arquivo.read_text(encoding="utf-8"))
    assert sorted(ids) == ["scdp_carga_completa", "scdp_carga_diaria"], f"dag_id inesperado ou duplicado: {ids}"


def test_configuracao_das_dags():
    diaria = (DAGS / "dag_carga_diaria.py").read_text(encoding="utf-8")
    completa = (DAGS / "dag_carga_completa.py").read_text(encoding="utf-8")
    for texto in (diaria, completa):
        assert "America/Sao_Paulo" in texto
        assert "catchup=False" in texto and "max_active_runs=1" in texto
    assert "skip_on_exit_code=CODIGO_OCUPADO" in diaria, "a diaria pode ser pulada quando a trava esta ocupada"
    assert "skip_on_exit_code" not in completa, "a completa nao pode ser pulada: falha e o retry tenta de novo"
    assert 'schedule="0 2 * * *"' in diaria
    assert 'schedule="30 3 1,11,21 * *"' in completa
