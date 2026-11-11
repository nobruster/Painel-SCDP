"""Integracao: papel scdp_leitura le a analitica e vw_ctl_*, nao escreve nem le staging/intermediaria (precisa de TEST_DATABASE_URL)."""
from pathlib import Path

import psycopg2
import pytest

PAPEL_SQL = Path(__file__).resolve().parent.parent / "3-Etl" / "dags" / "sql" / "papel_leitura.sql"


@pytest.fixture()
def papel(banco):
    banco.cur.execute(PAPEL_SQL.read_text(encoding="utf-8"))
    banco.conn.commit()
    try:
        banco.cur.execute("GRANT scdp_leitura TO CURRENT_USER")
        banco.conn.commit()
    except psycopg2.Error:
        banco.conn.rollback()
    return banco


def _como_leitura(banco, sql):
    cur = banco.cur
    cur.execute("SET ROLE scdp_leitura")
    try:
        cur.execute(sql)
        return cur.fetchall() if cur.description else None
    finally:
        banco.conn.rollback()
        cur.execute("RESET ROLE")
        banco.conn.commit()


def test_script_roda_duas_vezes(papel):
    papel.cur.execute(PAPEL_SQL.read_text(encoding="utf-8"))
    papel.conn.commit()
    papel.cur.execute("SELECT rolcanlogin, rolsuper FROM pg_roles WHERE rolname = 'scdp_leitura'")
    assert tuple(papel.cur.fetchone()) == (False, False)


@pytest.mark.parametrize("tabela", ["dim_data", "dim_orgao", "dim_ug", "dim_beneficiario", "dim_perfil_viagem",
                                    "fct_viagem", "obt_viagem"])
def test_select_na_analitica(papel, tabela):
    assert _como_leitura(papel, f"SELECT count(*) FROM @ANA@.{tabela}") is not None


def test_select_nas_views_de_controle(papel):
    assert _como_leitura(papel, "SELECT * FROM @STG@.vw_ctl_saude") is not None


@pytest.mark.parametrize("sql", [
    "INSERT INTO @ANA@.dim_data (data_key) VALUES ('1999-01-01')",
    "UPDATE @ANA@.dim_data SET ano = 0",
    "DELETE FROM @ANA@.dim_data",
    "TRUNCATE @ANA@.obt_viagem",
    "INSERT INTO @STG@.ctl_camada (camada) VALUES ('x')",
])
def test_escrita_negada(papel, sql):
    with pytest.raises(psycopg2.errors.InsufficientPrivilege):
        _como_leitura(papel, sql)


@pytest.mark.parametrize("sql", [
    "SELECT * FROM @STG@.stg_viagem",
    "SELECT * FROM @STG@.ctl_janela",
    "SELECT * FROM @INT@.int_viagem",
])
def test_sem_acesso_a_staging_nem_intermediaria(papel, sql):
    with pytest.raises(psycopg2.errors.InsufficientPrivilege):
        _como_leitura(papel, sql)
