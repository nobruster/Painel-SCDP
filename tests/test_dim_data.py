"""Integracao: dim_data cobre 2020-01-01 a 2035-12-31, sem duplicatas e idempotente (precisa de TEST_DATABASE_URL)."""
import datetime as dt

from scdp import carga

PRIMEIRA = dt.date(2020, 1, 1)
ULTIMA = dt.date(2035, 12, 31)
TOTAL_DIAS = (ULTIMA - PRIMEIRA).days + 1


def _resumo(cur):
    cur.execute("SELECT min(data_key), max(data_key), count(*), count(DISTINCT data_key) FROM @ANA@.dim_data")
    return tuple(cur.fetchone())


def test_dim_data_cobre_ate_2035(banco):
    assert _resumo(banco.cur) == (PRIMEIRA, ULTIMA, TOTAL_DIAS, TOTAL_DIAS)


def test_reaplicar_schema_nao_duplica_nem_apaga(banco):
    cur = banco.cur
    cur.execute("UPDATE @ANA@.dim_data SET fim_de_semana = NOT fim_de_semana WHERE data_key = '2035-12-31'")
    banco.conn.commit()
    assert carga.aplicar_schema(cur, forcar=True) is True
    banco.conn.commit()
    assert _resumo(cur) == (PRIMEIRA, ULTIMA, TOTAL_DIAS, TOTAL_DIAS)
    cur.execute("SELECT fim_de_semana FROM @ANA@.dim_data WHERE data_key = '2035-12-31'")
    assert cur.fetchone()[0] is True  # 2035-12-31 e segunda; o valor alterado a mao foi preservado


def test_extensao_em_banco_ja_carregado_com_ate_2030(banco):
    cur = banco.cur
    cur.execute("DELETE FROM @ANA@.dim_data WHERE data_key > '2030-12-31'")
    banco.conn.commit()
    carga.aplicar_schema(cur, forcar=True)
    banco.conn.commit()
    assert _resumo(cur) == (PRIMEIRA, ULTIMA, TOTAL_DIAS, TOTAL_DIAS)
