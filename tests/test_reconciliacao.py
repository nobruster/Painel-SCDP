"""O gate precisa acusar: cada defeito injetado muda o veredito (precisa de TEST_DATABASE_URL)."""
import datetime as dt

from helpers import FakeExtrator, viagem
from scdp import reconciliacao, transformacao

IDA = RET = dt.date(2026, 8, 1)


def carregar(banco, dados):
    banco.pipeline(FakeExtrator(lambda ida, ret, n: dados)).processar_janela(IDA, RET, None)
    transformacao.atualizar_analitica(banco.cur)


def test_banco_vazio_nao_e_medido(banco):
    assert reconciliacao.reconciliar(banco.cur).veredito == reconciliacao.NAO_MEDIDO


def test_carga_consistente_passa(banco):
    carregar(banco, [viagem(1, "2026-08-03", "2026-08-04", 1000.0, 600.0, 400.0),
                     viagem(2, "2026-08-10", "2026-08-12", 1500.0, 500.0, 900.0, outros=100.0)])
    r = reconciliacao.reconciliar(banco.cur)
    assert r.veredito == reconciliacao.OK, r.motivos
    assert r.medidas["outros_gastos_positivo"] == 1


def test_valor_adulterado_na_intermediaria_e_acusado(banco):
    carregar(banco, [viagem(1, "2026-08-03", "2026-08-04", 1000.0, 600.0, 400.0)])
    banco.cur.execute("UPDATE @INT@.int_viagem SET valor_total_viagem = valor_total_viagem + 0.01")
    r = reconciliacao.reconciliar(banco.cur)
    assert r.veredito == reconciliacao.DIVERGENTE
    assert r.medidas["total_nao_fecha"] == 1


def test_linha_perdida_na_analitica_e_acusada(banco):
    carregar(banco, [viagem(1, "2026-08-03", "2026-08-04", 1000.0, 600.0, 400.0),
                     viagem(2, "2026-08-10", "2026-08-12", 300.0, 0.0, 300.0)])
    banco.cur.execute("DELETE FROM @ANA@.fct_viagem WHERE viagem_id = (SELECT min(viagem_id) FROM @ANA@.fct_viagem)")
    assert reconciliacao.reconciliar(banco.cur).veredito == reconciliacao.DIVERGENTE
