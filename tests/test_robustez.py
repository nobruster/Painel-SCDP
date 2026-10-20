"""Integracao: dados sujos, ids repetidos, trava de execucao simultanea, schema idempotente e queda de conexao."""
import dataclasses
import datetime as dt
import os

import pytest

from helpers import FakeExtrator, viagem
from scdp import carga, transformacao
from scdp.controle import Controle
from scdp.pipeline import CODIGO_OCUPADO, ErroFatal, Pipeline

IDA = RET = dt.date(2026, 8, 1)
HOJE = dt.date(2026, 10, 19)
DESDE = dt.date(2026, 10, 1)


def test_dados_sujos_viram_null_e_nao_derrubam_a_janela(banco):
    sujo = viagem(1, "", "2026-08-04", 1.0, 1.0, 0.0)
    sujo["valorTotalViagem"] = "abc"
    sujo["valorTotalPassagem"] = "100000000000000"
    sujo["viagem"]["ano"] = ""
    sujo["dataFimAfastamento"] = "04/08/2026"
    bom = viagem(2, "2026-08-10", "2026-08-12", 500.0, 500.0, 0.0)
    pipe = banco.pipeline(FakeExtrator(lambda ida, ret, n: [sujo, bom]))

    r = pipe.processar_janela(IDA, RET, None)
    assert (r.ok, r.novos) == (True, 2)
    cur = banco.cur
    cur.execute("SELECT data_inicio, data_fim, ano, valor_total_viagem, valor_passagem, dias_afastamento FROM @INT@.int_viagem WHERE id = 1")
    assert cur.fetchone() == (None, None, None, None, None, None)
    cur.execute("SELECT valor_total_viagem, dias_afastamento FROM @INT@.int_viagem WHERE id = 2")
    assert cur.fetchone() == (500.0, 3)
    cur.execute("SELECT payload->>'valorTotalViagem' FROM @STG@.stg_viagem WHERE id = 1")
    assert cur.fetchone()[0] == "abc", "a staging guarda o JSON como veio"
    assert transformacao.atualizar_analitica(cur) == 2
    banco.conn.commit()
    cur.execute("SELECT count(*) FROM @ANA@.obt_viagem")
    assert cur.fetchone()[0] == 2


def test_id_repetido_na_mesma_janela_e_descartado_com_aviso(banco):
    v = viagem(1, "2026-08-03", "2026-08-04", 100.0, 100.0, 0.0)
    pipe = banco.pipeline(FakeExtrator(lambda ida, ret, n: [v, dict(v)]))
    r = pipe.processar_janela(IDA, RET, None)
    assert (r.ok, r.qtd, r.novos) == (True, 1, 1)
    assert "repetidos" in r.aviso


def test_so_uma_execucao_por_vez_por_orgao(banco):
    url = os.environ["TEST_DATABASE_URL"]
    segunda = carga.conectar(dataclasses.replace(banco.cfg, database_url=url))
    try:
        pipe2 = Pipeline(banco.cfg, segunda, FakeExtrator(lambda ida, ret, n: []),
                         Controle(segunda.cursor(), segunda, banco.cfg.orgao), dormir=lambda s: None)
        pipe1 = banco.pipeline(FakeExtrator(lambda ida, ret, n: []))
        assert pipe1._obter_trava() is True
        assert pipe2.executar("diario", DESDE, HOJE) == CODIGO_OCUPADO
        assert pipe2.reconstruir() == CODIGO_OCUPADO
        pipe1._liberar_trava()
        assert pipe2.executar("diario", DESDE, HOJE) == 0
    finally:
        segunda.close()


def test_schema_pode_ser_aplicado_varias_vezes(banco):
    carga.aplicar_schema(banco.cur)
    banco.conn.commit()
    carga.aplicar_schema(banco.cur)
    banco.conn.commit()
    banco.cur.execute("SELECT count(*) FROM information_schema.columns WHERE table_schema = %s AND table_name = 'ctl_execucao' AND column_name = 'status'",
                      (banco.cfg.schema_stg,))
    assert banco.cur.fetchone()[0] == 1


def test_conexao_perdida_aborta_em_vez_de_continuar(banco):
    def derruba(ida, ret, n):
        banco.conn.close()
        return RuntimeError("falha depois de a conexao cair")

    pipe = banco.pipeline(FakeExtrator(derruba))
    with pytest.raises(ErroFatal):
        pipe.processar_janela(IDA, RET, None)


def test_segredo_nao_vai_para_a_tabela_de_erros(banco):
    cfg = dataclasses.replace(banco.cfg, pg_password="s3nha-secreta")
    pipe = Pipeline(cfg, banco.conn, FakeExtrator(lambda ida, ret, n: RuntimeError("falha com s3nha-secreta e chave-de-teste")),
                    Controle(banco.cur, banco.conn, cfg.orgao, sanitizar=cfg.sanitizar), dormir=lambda s: None)
    pipe.processar_janela(IDA, RET, None)
    banco.cur.execute("SELECT mensagem FROM @STG@.ctl_erro")
    msg = banco.cur.fetchone()[0]
    assert "s3nha-secreta" not in msg and "chave-de-teste" not in msg
    banco.cur.execute("SELECT erro FROM @STG@.ctl_janela")
    assert "s3nha-secreta" not in banco.cur.fetchone()[0]
