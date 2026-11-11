import datetime as dt

from helpers import FakeExtrator, viagem

OUT = dt.date(2026, 10, 1)
HOJE = dt.date(2026, 10, 19)


def dez_viagens():
    return [viagem(i, "2026-10-05", "2026-10-06", 10.0, 10.0, 0.0) for i in range(1, 11)]


def aviso_e_contagens(banco):
    banco.cur.execute("SELECT status, aviso, qtd_api, qtd_carregada FROM @STG@.ctl_janela WHERE ida_mes=%s AND retorno_mes=%s",
                      (OUT, OUT))
    return banco.cur.fetchone()


def test_queda_vira_aviso_e_nao_apaga_viagens(banco):
    pipe = banco.pipeline(FakeExtrator(lambda ida, ret, n: dez_viagens()))
    assert pipe.processar_janela(OUT, OUT, None).ok
    sete = dez_viagens()[:7]
    pipe = banco.pipeline(FakeExtrator(lambda ida, ret, n: sete))
    r = pipe.processar_janela(OUT, OUT, None)
    assert r.ok
    status, aviso, qtd_api, carregadas = aviso_e_contagens(banco)
    assert status == "OK" and "queda de 10 para 7" in aviso and qtd_api == 7
    banco.cur.execute("SELECT count(*) FROM @STG@.stg_viagem")
    assert banco.cur.fetchone()[0] == 10


def test_queda_que_se_recupera_na_releitura_nao_gera_aviso(banco):
    banco.pipeline(FakeExtrator(lambda ida, ret, n: dez_viagens())).processar_janela(OUT, OUT, None)
    pipe = banco.pipeline(FakeExtrator(lambda ida, ret, n: dez_viagens()[:7] if n == 1 else dez_viagens()))
    pipe.processar_janela(OUT, OUT, None)
    assert aviso_e_contagens(banco)[1] is None


def test_sem_queda_nao_ha_aviso(banco):
    pipe = banco.pipeline(FakeExtrator(lambda ida, ret, n: dez_viagens()))
    pipe.processar_janela(OUT, OUT, None)
    pipe.processar_janela(OUT, OUT, None)
    assert aviso_e_contagens(banco)[1] is None
