"""Integracao: carga de varios orgaos (cada um com suas janelas e controle) e de um orgao so."""
import dataclasses
import datetime as dt

from helpers import FakeExtrator, viagem
from scdp.pipeline import Pipeline

HOJE = dt.date(2026, 10, 19)
DESDE = dt.date(2026, 10, 1)
OUT = dt.date(2026, 10, 1)
JANELAS_PLANEJADAS = 39

DADOS = {
    "33000": [viagem(1, "2026-10-05", "2026-10-06", 100.0, 100.0, 0.0, orgao="33000")],
    "37202": [viagem(2, "2026-10-08", "2026-10-09", 50.0, 0.0, 50.0, orgao="37202"),
              viagem(3, "2026-10-10", "2026-10-11", 20.0, 0.0, 20.0, orgao="37202")],
}


def pipeline_com_orgaos(banco, orgaos):
    cfg = dataclasses.replace(banco.cfg, orgao=",".join(orgaos))
    extratores = {}

    def fabrica(cod):
        if cod not in extratores:
            extratores[cod] = FakeExtrator(lambda ida, ret, n, cod=cod: DADOS[cod] if (ida, ret) == (OUT, OUT) else [])
        return extratores[cod]

    return Pipeline(cfg, banco.conn, fabrica(orgaos[0]), banco.controle, dormir=lambda s: None, extrator_por_orgao=fabrica), extratores


def test_cada_orgao_tem_suas_janelas_e_nenhuma_e_lida_duas_vezes(banco):
    pipe, extratores = pipeline_com_orgaos(banco, ["33000", "37202"])
    assert pipe.executar("diario", DESDE, HOJE) == 0
    banco.cur.execute("SELECT orgao, count(*), sum(qtd_api) FROM @STG@.ctl_janela GROUP BY orgao ORDER BY orgao")
    assert banco.cur.fetchall() == [("33000", JANELAS_PLANEJADAS, 1), ("37202", JANELAS_PLANEJADAS, 2)]
    for ext in extratores.values():
        assert set(ext.chamadas.values()) == {1}
        assert len(ext.chamadas) == JANELAS_PLANEJADAS
    banco.cur.execute("SELECT count(*) FROM @ANA@.obt_viagem")
    assert banco.cur.fetchone()[0] == 3
    banco.cur.execute("SELECT janelas_total, janelas_lidas, janelas_erro, novos, status FROM @STG@.ctl_execucao")
    assert banco.cur.fetchall() == [(2 * JANELAS_PLANEJADAS, 2 * JANELAS_PLANEJADAS, 0, 3, "CONCLUIDA")]


def test_falha_em_um_orgao_nao_apaga_o_outro_e_deixa_erro_aberto(banco):
    cfg = dataclasses.replace(banco.cfg, orgao="33000,37202")

    def fabrica(cod):
        def resposta(ida, ret, n):
            if cod == "37202" and (ida, ret) == (OUT, OUT):
                return RuntimeError("API indisponivel")
            return DADOS[cod] if (ida, ret) == (OUT, OUT) else []
        return FakeExtrator(resposta)

    pipe = Pipeline(cfg, banco.conn, fabrica("33000"), banco.controle, dormir=lambda s: None, extrator_por_orgao=fabrica)
    assert pipe.executar("diario", DESDE, HOJE) == 1
    banco.cur.execute("SELECT orgao, ida_mes FROM @STG@.ctl_erro")
    assert banco.cur.fetchall() == [("37202", OUT)]
    banco.cur.execute("SELECT orgao, count(*) FROM @STG@.ctl_janela WHERE status <> 'OK' GROUP BY orgao")
    assert banco.cur.fetchall() == [("37202", 1)]


def test_um_orgao_continua_igual(banco):
    pipe, extratores = pipeline_com_orgaos(banco, ["33000"])
    assert pipe.executar("diario", DESDE, HOJE) == 0
    banco.cur.execute("SELECT DISTINCT orgao FROM @STG@.ctl_janela")
    assert banco.cur.fetchall() == [("33000",)]
    banco.cur.execute("SELECT janelas_total, status FROM @STG@.ctl_execucao")
    assert banco.cur.fetchall() == [(JANELAS_PLANEJADAS, "CONCLUIDA")]


def test_sem_fabrica_um_orgao_usa_o_extrator_recebido(banco):
    extrator = FakeExtrator(lambda ida, ret, n: DADOS["33000"] if (ida, ret) == (OUT, OUT) else [])
    assert banco.pipeline(extrator).executar("diario", DESDE, HOJE) == 0
    assert len(extrator.chamadas) == JANELAS_PLANEJADAS
