"""Integracao: execucao completa (varias janelas), retentativas, abortar e retomar de onde parou."""
import datetime as dt

from helpers import FakeExtrator, viagem
from scdp.extracao import ErroPermanente

HOJE = dt.date(2026, 10, 19)
DESDE = dt.date(2026, 10, 1)
OUT = dt.date(2026, 10, 1)
NOV = dt.date(2026, 11, 1)
JANELAS_PLANEJADAS = 39

DADOS_OUT = [viagem(1, "2026-10-05", "2026-10-06", 100.0, 100.0, 0.0), viagem(2, "2026-10-08", "2026-10-09", 50.0, 0.0, 50.0)]
DADOS_NOV = [viagem(3, "2026-11-05", "2026-11-06", 80.0, 80.0, 0.0)]


def resposta_base(ida, ret):
    if (ida, ret) == (OUT, OUT):
        return DADOS_OUT
    if (ida, ret) == (NOV, NOV):
        return DADOS_NOV
    return []


def execucao(cur):
    cur.execute("SELECT status, janelas_lidas, janelas_erro, novos FROM @STG@.ctl_execucao ORDER BY id DESC LIMIT 1")
    return cur.fetchone()


def test_execucao_limpa(banco):
    pipe = banco.pipeline(FakeExtrator(lambda ida, ret, n: resposta_base(ida, ret)))
    assert pipe.executar("diario", DESDE, HOJE) == 0
    assert execucao(banco.cur) == ("CONCLUIDA", JANELAS_PLANEJADAS, 0, 3)
    banco.cur.execute("SELECT count(*) FROM @ANA@.obt_viagem")
    assert banco.cur.fetchone()[0] == 3
    banco.cur.execute("SELECT erros_abertos, janelas_pendentes FROM @STG@.vw_ctl_saude")
    assert banco.cur.fetchone() == (0, 0)


def test_janela_que_falha_e_corrigida_na_retentativa(banco):
    def resposta(ida, ret, n):
        if (ida, ret) == (NOV, NOV) and n == 1:
            return RuntimeError("API indisponivel")
        return resposta_base(ida, ret)

    pipe = banco.pipeline(FakeExtrator(resposta))
    assert pipe.executar("diario", DESDE, HOJE) == 0
    assert execucao(banco.cur)[0] == "CONCLUIDA"
    banco.cur.execute("SELECT count(*) FROM @STG@.ctl_erro")
    assert banco.cur.fetchone()[0] == 0
    banco.cur.execute("SELECT etapa, tentativas FROM @STG@.ctl_erro_historico")
    assert banco.cur.fetchall() == [("api", 1)]


def test_falha_permanente_fica_registrada_e_a_execucao_termina_com_erros(banco, cfg):
    def resposta(ida, ret, n):
        return RuntimeError("API indisponivel") if (ida, ret) == (NOV, NOV) else resposta_base(ida, ret)

    pipe = banco.pipeline(FakeExtrator(resposta))
    assert pipe.executar("diario", DESDE, HOJE) == 1
    assert execucao(banco.cur)[0:3] == ("COM_ERROS", JANELAS_PLANEJADAS, 1)
    banco.cur.execute("SELECT etapa, tentativas, ida_mes FROM @STG@.ctl_erro")
    assert banco.cur.fetchall() == [("api", 1 + cfg.rodadas_retentativa, NOV)]


def test_chave_invalida_aborta(banco):
    pipe = banco.pipeline(FakeExtrator(lambda ida, ret, n: ErroPermanente(401, "chave invalida")))
    assert pipe.executar("diario", DESDE, HOJE) == 1
    assert execucao(banco.cur)[0] == "ABORTADA"


def test_proxima_execucao_retoma_pela_janela_com_erro(banco):
    def falha_em_nov(ida, ret, n):
        return RuntimeError("API indisponivel") if (ida, ret) == (NOV, NOV) else resposta_base(ida, ret)

    assert banco.pipeline(FakeExtrator(falha_em_nov)).executar("diario", DESDE, HOJE) == 1

    corrigido = FakeExtrator(lambda ida, ret, n: resposta_base(ida, ret))
    assert banco.pipeline(corrigido).executar("diario", DESDE, HOJE) == 0
    assert corrigido.ordem[0] == (NOV, NOV)
    assert execucao(banco.cur)[0] == "CONCLUIDA"
    banco.cur.execute("SELECT count(*) FROM @STG@.ctl_erro")
    assert banco.cur.fetchone()[0] == 0
    banco.cur.execute("SELECT count(*) FROM @STG@.ctl_erro_historico")
    assert banco.cur.fetchone()[0] == 1
