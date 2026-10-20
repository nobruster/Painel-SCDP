"""Integracao: dados sujos, ids repetidos, trava de execucao simultanea, schema idempotente e queda de conexao."""
import dataclasses
import datetime as dt
import os

import psycopg2
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


def test_so_uma_execucao_por_vez_por_orgao(banco, caplog):
    url = os.environ["TEST_DATABASE_URL"]
    segunda = carga.conectar(dataclasses.replace(banco.cfg, database_url=url))
    try:
        pipe2 = Pipeline(banco.cfg, segunda, FakeExtrator(lambda ida, ret, n: []),
                         Controle(segunda.cursor(), segunda, banco.cfg.orgao), dormir=lambda s: None)
        pipe1 = banco.pipeline(FakeExtrator(lambda ida, ret, n: []))
        assert pipe1._obter_trava() is True
        assert pipe2.executar("diario", DESDE, HOJE) == CODIGO_OCUPADO
        assert "trava com pid" in caplog.text, "o log precisa dizer quem segura a trava"
        assert pipe2.reconstruir() == CODIGO_OCUPADO
        pipe1._liberar_trava()
        assert pipe2.executar("diario", DESDE, HOJE) == 0
    finally:
        segunda.close()


def test_schema_so_e_reaplicado_quando_o_arquivo_muda_e_forcar_e_idempotente(banco):
    assert carga.aplicar_schema(banco.cur) is False, "a versao ja foi aplicada pela fixture"
    assert carga.aplicar_schema(banco.cur, forcar=True) is True
    banco.conn.commit()
    assert carga.aplicar_schema(banco.cur, forcar=True) is True
    banco.conn.commit()
    banco.cur.execute("SELECT count(*) FROM information_schema.columns WHERE table_schema = %s AND table_name = 'ctl_execucao' AND column_name = 'status'",
                      (banco.cfg.schema_stg,))
    assert banco.cur.fetchone()[0] == 1
    banco.cur.execute("UPDATE @STG@.ctl_schema SET versao = 'antiga'")
    assert carga.aplicar_schema(banco.cur) is True


def test_marcadores_de_schema_nao_alteram_os_dados_gravados(banco):
    v = viagem(5, "2026-08-03", "2026-08-04", 10.0, 10.0, 0.0)
    v["viagem"]["motivo"] = "texto com @INT@ e @STG@ e @ANA@ dentro"
    pipe = banco.pipeline(FakeExtrator(lambda ida, ret, n: [v]))
    pipe.processar_janela(IDA, RET, None)
    banco.cur.execute("SELECT payload->'viagem'->>'motivo' FROM @STG@.stg_viagem WHERE id = 5")
    assert banco.cur.fetchone()[0] == "texto com @INT@ e @STG@ e @ANA@ dentro"


def test_aviso_quando_a_conversao_tolerante_zera_data_ou_valor(banco):
    sujo = viagem(1, "", "2026-08-04", 1.0, 1.0, 0.0)
    pipe = banco.pipeline(FakeExtrator(lambda ida, ret, n: [sujo]))
    r = pipe.processar_janela(IDA, RET, None)
    assert r.ok and "ausente ou invalido" in r.aviso
    banco.cur.execute("SELECT aviso FROM @STG@.ctl_janela")
    assert "ausente ou invalido" in banco.cur.fetchone()[0]


def test_valor_com_mais_de_duas_casas_e_arredondado_de_forma_explicita(banco):
    v = viagem(1, "2026-08-03", "2026-08-04", 1.0, 1.0, 0.0)
    v["valorTotalViagem"] = "10.456"
    pipe = banco.pipeline(FakeExtrator(lambda ida, ret, n: [v]))
    pipe.processar_janela(IDA, RET, None)
    banco.cur.execute("SELECT valor_total_viagem FROM @INT@.int_viagem WHERE id = 1")
    assert float(banco.cur.fetchone()[0]) == 10.46


def test_numero_que_estoura_so_depois_de_arredondar_vira_null(banco):
    v = viagem(1, "2026-08-03", "2026-08-04", 1.0, 1.0, 0.0)
    v["valorTotalViagem"] = "9999999999999.995"
    pipe = banco.pipeline(FakeExtrator(lambda ida, ret, n: [v]))
    r = pipe.processar_janela(IDA, RET, None)
    assert r.ok
    banco.cur.execute("SELECT valor_total_viagem FROM @INT@.int_viagem WHERE id = 1")
    assert banco.cur.fetchone()[0] is None


def test_erro_real_de_cast_do_postgres_nao_grava_o_valor_ofensivo(banco, monkeypatch):
    pipe = banco.pipeline(FakeExtrator(lambda ida, ret, n: [viagem(1, "2026-08-03", "2026-08-04", 1.0, 1.0, 0.0)]))

    def quebra(cur, ids=None):
        cur.execute("SELECT 'FULANO DE TAL'::bigint")

    monkeypatch.setattr(transformacao, "atualizar_intermediaria", quebra)
    assert pipe.processar_janela(IDA, RET, None).ok is False
    banco.cur.execute("SELECT mensagem FROM @STG@.ctl_erro")
    msg = banco.cur.fetchone()[0]
    assert "FULANO" not in msg and "invalid input syntax" in msg
    banco.cur.execute("SELECT erro FROM @STG@.ctl_janela")
    assert "FULANO" not in banco.cur.fetchone()[0]


def test_hash_do_schema_inclui_os_nomes_dos_schemas(banco):
    url = os.environ["TEST_DATABASE_URL"]
    outro = dataclasses.replace(banco.cfg, database_url=url, schema_int="zz_teste_int2")
    conn2 = carga.conectar(outro)
    try:
        cur2 = conn2.cursor()
        cur2.execute("CREATE SCHEMA IF NOT EXISTS zz_teste_int2")
        conn2.commit()
        assert carga.aplicar_schema(cur2) is True, "mudou SCHEMA_INT: o DDL precisa rodar mesmo com o mesmo arquivo"
        conn2.commit()
        cur2.execute("SELECT to_regclass('zz_teste_int2.int_viagem') IS NOT NULL")
        assert cur2.fetchone()[0] is True
    finally:
        conn2.rollback()
        conn2.cursor().execute("DROP SCHEMA IF EXISTS zz_teste_int2 CASCADE")
        conn2.commit()
        conn2.close()


def test_erro_de_banco_fora_da_janela_fecha_a_execucao_como_abortada(banco, monkeypatch):
    pipe = banco.pipeline(FakeExtrator(lambda ida, ret, n: []))

    def cai(*a, **k):
        raise psycopg2.OperationalError("servidor caiu")

    monkeypatch.setattr(pipe, "processar_janela", cai)
    assert pipe.executar("diario", DESDE, HOJE) == 1
    banco.cur.execute("SELECT status, fim IS NOT NULL FROM @STG@.ctl_execucao ORDER BY id DESC LIMIT 1")
    assert banco.cur.fetchone() == ("ABORTADA", True)


def test_chave_da_trava_considera_os_tres_schemas(cfg):
    from unittest.mock import MagicMock
    a = Pipeline(cfg, MagicMock(), None, None)
    b = Pipeline(dataclasses.replace(cfg, schema_ana="zz_teste_outra"), MagicMock(), None, None)
    assert a._chave_trava() != b._chave_trava()


def test_execucao_orfa_e_marcada_na_hora_porque_a_trava_esta_em_maos(banco):
    cur = banco.cur
    cur.execute("INSERT INTO @STG@.ctl_execucao (inicio, modo, status) VALUES (now(), 'diario', 'EXECUTANDO') RETURNING id")
    orfa = cur.fetchone()[0]
    banco.conn.commit()
    pipe = banco.pipeline(FakeExtrator(lambda ida, ret, n: []))
    assert pipe.executar("diario", DESDE, HOJE) == 0
    cur.execute("SELECT status FROM @STG@.ctl_execucao WHERE id = %s", (orfa,))
    assert cur.fetchone()[0] == "INTERROMPIDA"
    cur.execute("SELECT count(*) FROM @STG@.ctl_erro")
    assert cur.fetchone()[0] == 0
    cur.execute("SELECT count(*) FROM @STG@.ctl_erro_historico WHERE etapa = 'execucao'")
    assert cur.fetchone()[0] == 1


def test_sigterm_marca_a_execucao_como_interrompida_e_libera_a_trava(banco):
    def morre(ida, ret, n):
        raise KeyboardInterrupt("sinal 15")

    pipe = banco.pipeline(FakeExtrator(morre))
    with pytest.raises(KeyboardInterrupt):
        pipe.executar("diario", DESDE, HOJE)
    banco.cur.execute("SELECT status, fim IS NOT NULL FROM @STG@.ctl_execucao ORDER BY id DESC LIMIT 1")
    assert banco.cur.fetchone() == ("INTERROMPIDA", True)
    assert pipe._obter_trava() is True


def test_trava_e_liberada_mesmo_quando_a_execucao_levanta_excecao(banco, monkeypatch):
    url = os.environ["TEST_DATABASE_URL"]
    pipe = banco.pipeline(FakeExtrator(lambda ida, ret, n: []))

    def quebra(*a, **k):
        raise RuntimeError("bug")

    monkeypatch.setattr(pipe, "_executar", quebra)
    with pytest.raises(RuntimeError):
        pipe.executar("diario", DESDE, HOJE)
    outra = carga.conectar(dataclasses.replace(banco.cfg, database_url=url))
    try:
        pipe2 = Pipeline(banco.cfg, outra, FakeExtrator(lambda ida, ret, n: []),
                         Controle(outra.cursor(), outra, banco.cfg.orgao), dormir=lambda s: None)
        assert pipe2._obter_trava() is True
    finally:
        outra.close()


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
