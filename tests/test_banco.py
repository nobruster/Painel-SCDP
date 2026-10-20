"""Integracao: carga incremental ponta a ponta nas tres camadas (precisa de TEST_DATABASE_URL)."""
import datetime as dt

from helpers import FakeExtrator, viagem
from scdp import transformacao

IDA = RET = dt.date(2026, 8, 1)
JA_LIDA = {"status": "OK", "qtd_api": 3, "fim": None}


def test_carga_incremental_ponta_a_ponta(banco):
    cur, cfg = banco.cur, banco.cfg
    dados = [
        viagem(1, "2026-08-03", "2026-08-04", 1000.0, 600.0, 400.0),
        viagem(2, "2026-08-10", "2026-08-12", 1500.0, 500.0, 900.0, outros=100.0),
        viagem(3, "2026-08-20", "2026-08-21", 300.0, 0.0, 300.0),
    ]
    pipe = banco.pipeline(FakeExtrator(lambda ida, ret, n: dados))

    r = pipe.processar_janela(IDA, RET, None)
    assert (r.ok, r.qtd, r.novos, r.alterados) == (True, 3, 3, 0)

    r = pipe.processar_janela(IDA, RET, JA_LIDA)
    assert (r.ok, r.novos, r.alterados) == (True, 0, 0)

    dados[0] = {**dados[0], "valorTotalViagem": 1100.0, "valorTotalPassagem": 700.0}
    r = pipe.processar_janela(IDA, RET, JA_LIDA)
    assert (r.ok, r.novos, r.alterados) == (True, 0, 1)

    dados.append(viagem(4, "2026-08-25", "2026-08-26", 200.0, 0.0, 200.0))
    r = pipe.processar_janela(IDA, RET, JA_LIDA)
    assert (r.ok, r.novos, r.alterados) == (True, 1, 0)

    cur.execute("SELECT count(*) FROM @STG@.stg_viagem")
    assert cur.fetchone()[0] == 4
    cur.execute("SELECT count(*) FROM @INT@.int_viagem")
    assert cur.fetchone()[0] == 4
    cur.execute("SELECT valor_outros_gastos, dias_afastamento FROM @INT@.int_viagem WHERE id = 2")
    assert cur.fetchone() == (100.0, 3)

    assert transformacao.atualizar_analitica(cur) == 4
    banco.conn.commit()
    for tabela in ("fct_viagem", "obt_viagem"):
        cur.execute(f"SELECT count(*) FROM @ANA@.{tabela}")
        assert cur.fetchone()[0] == 4
        cur.execute("SELECT 1 FROM information_schema.columns WHERE table_schema=%s AND table_name=%s AND column_name='motivo'",
                    (cfg.schema_ana, tabela))
        assert cur.fetchone() is None, "motivo nao pode estar na analitica"
    cur.execute("SELECT valor_total_viagem FROM @ANA@.obt_viagem WHERE viagem_id = 1")
    assert float(cur.fetchone()[0]) == 1100.0
    cur.execute("SELECT count(*) FROM @ANA@.dim_orgao")
    assert cur.fetchone()[0] == 1

    assert transformacao.atualizar_analitica(cur) == 0, "sem mudanca na intermediaria, nada a processar"
    banco.conn.commit()
    transformacao.atualizar_analitica(cur, tudo=True)
    banco.conn.commit()
    assert transformacao.atualizar_analitica(cur) == 0, "depois de reconstruir tudo, o empate de timestamps nao reprocessa"
    banco.conn.commit()

    cur.execute("UPDATE @INT@.int_viagem SET orgao_nome = 'Nome Novo', atualizado_em = now() WHERE id = 1")
    banco.conn.commit()
    transformacao.atualizar_analitica(cur)
    banco.conn.commit()
    cur.execute("SELECT DISTINCT orgao_nome FROM @ANA@.obt_viagem")
    assert cur.fetchall() == [("Nome Novo",)]

    cur.execute("SELECT status, qtd_api, qtd_carregada FROM @STG@.ctl_janela")
    assert cur.fetchone() == ("OK", 4, 4)


def test_staging_guarda_o_json_como_veio(banco):
    original = viagem(7, "2026-08-03", "2026-08-04", 10.0, 10.0, 0.0)
    pipe = banco.pipeline(FakeExtrator(lambda ida, ret, n: [original]))
    pipe.processar_janela(IDA, RET, None)
    banco.cur.execute("SELECT payload FROM @STG@.stg_viagem WHERE id = 7")
    assert banco.cur.fetchone()[0] == original
