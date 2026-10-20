"""Integracao: registro de erros, resolucao (saem de ctl_erro quando corrigidos) e visoes de observabilidade."""
import datetime as dt

import pytest

from helpers import FakeExtrator, viagem
from scdp import transformacao
from scdp.extracao import ErroPermanente
from scdp.pipeline import ErroFatal

IDA = RET = dt.date(2026, 8, 1)
ERRO = {"status": "ERRO", "qtd_api": None, "fim": None}


def abertos(cur):
    cur.execute("SELECT etapa, codigo, tentativas FROM @STG@.ctl_erro ORDER BY chave")
    return cur.fetchall()


def test_erro_de_api_e_registrado_e_sai_da_tabela_quando_corrigido(banco):
    cur = banco.cur
    dados = [viagem(1, "2026-08-03", "2026-08-04", 100.0, 100.0, 0.0)]
    extrator = FakeExtrator(lambda ida, ret, n: RuntimeError("API indisponivel") if n <= 2 else dados)
    pipe = banco.pipeline(extrator)

    assert pipe.processar_janela(IDA, RET, None).ok is False
    assert abertos(cur) == [("api", "RuntimeError", 1)]
    cur.execute("SELECT status FROM @STG@.ctl_janela")
    assert cur.fetchone()[0] == "ERRO"

    assert pipe.processar_janela(IDA, RET, ERRO).ok is False
    assert abertos(cur) == [("api", "RuntimeError", 2)]

    assert pipe.processar_janela(IDA, RET, ERRO).ok is True
    assert abertos(cur) == []
    cur.execute("SELECT etapa, tentativas, resolvido_em IS NOT NULL FROM @STG@.ctl_erro_historico")
    assert cur.fetchall() == [("api", 2, True)]
    cur.execute("SELECT status FROM @STG@.ctl_janela")
    assert cur.fetchone()[0] == "OK"


def test_erro_400_e_registrado_com_codigo_e_nao_derruba(banco):
    pipe = banco.pipeline(FakeExtrator(lambda ida, ret, n: ErroPermanente(400, "periodo maior que 1 mes")))
    assert pipe.processar_janela(IDA, RET, None).ok is False
    assert abertos(banco.cur) == [("api", "400", 1)]


def test_erro_401_aborta_a_execucao(banco):
    pipe = banco.pipeline(FakeExtrator(lambda ida, ret, n: ErroPermanente(401, "chave invalida")))
    with pytest.raises(ErroFatal):
        pipe.processar_janela(IDA, RET, None)
    assert abertos(banco.cur) == [("api", "401", 1)]


def test_erro_de_banco_e_registrado_na_etapa_banco(banco):
    pipe = banco.pipeline(FakeExtrator(lambda ida, ret, n: [{"sem_id": 1}]))
    assert pipe.processar_janela(IDA, RET, None).ok is False
    assert abertos(banco.cur) == [("banco", "KeyError", 1)]


def test_execucao_interrompida_e_marcada_e_resolvida(banco):
    cur, controle = banco.cur, banco.controle
    cur.execute("INSERT INTO @STG@.ctl_execucao (inicio, modo) VALUES (now() - interval '13 hours', 'diario') RETURNING id")
    antiga = cur.fetchone()[0]
    cur.execute("INSERT INTO @STG@.ctl_execucao (inicio, modo) VALUES (now(), 'diario') RETURNING id")
    recente = cur.fetchone()[0]
    banco.conn.commit()

    controle.marcar_execucoes_interrompidas(12)
    cur.execute("SELECT id, status FROM @STG@.ctl_execucao ORDER BY id")
    assert cur.fetchall() == [(antiga, "INTERROMPIDA"), (recente, None)]
    assert abertos(cur) == [("execucao", None, 1)]

    controle.resolver_erros(None, None, etapa="execucao")
    banco.conn.commit()
    assert abertos(cur) == []
    cur.execute("SELECT count(*) FROM @STG@.ctl_erro_historico WHERE etapa = 'execucao'")
    assert cur.fetchone()[0] == 1


def test_erro_da_analitica_e_registrado_e_resolvido(banco, monkeypatch):
    pipe = banco.pipeline(FakeExtrator(lambda ida, ret, n: []))

    def quebra(cur, tudo=False):
        raise RuntimeError("falha na analitica")

    monkeypatch.setattr(transformacao, "atualizar_analitica", quebra)
    assert pipe.atualizar_analitica_registrando() == (0, False)
    assert abertos(banco.cur) == [("analitica", "RuntimeError", 1)]

    monkeypatch.setattr(transformacao, "atualizar_analitica", lambda cur, tudo=False: 5)
    assert pipe.atualizar_analitica_registrando() == (5, True)
    assert abertos(banco.cur) == []


def test_visoes_de_observabilidade_no_schema_staging(banco):
    cur, cfg = banco.cur, banco.cfg
    pipe = banco.pipeline(FakeExtrator(lambda ida, ret, n: RuntimeError("API indisponivel")))
    pipe.processar_janela(IDA, RET, None)
    cur.execute("SELECT erros_abertos, janelas_pendentes, janelas_total FROM @STG@.vw_ctl_saude")
    assert cur.fetchone() == (1, 1, 1)
    cur.execute("SELECT etapa, horas_aberto >= 0 FROM @STG@.vw_ctl_erros_abertos")
    assert cur.fetchall() == [("api", True)]
    cur.execute("SELECT count(*) FROM @STG@.vw_ctl_execucoes")
    assert cur.fetchone()[0] == 0
    cur.execute("""SELECT table_schema FROM information_schema.tables
                   WHERE table_schema IN (%s, %s, %s)
                     AND table_name IN ('ctl_erro', 'ctl_erro_historico', 'ctl_janela', 'ctl_execucao', 'ctl_camada')
                   GROUP BY 1""", (cfg.schema_stg, cfg.schema_int, cfg.schema_ana))
    assert cur.fetchall() == [(cfg.schema_stg,)]
