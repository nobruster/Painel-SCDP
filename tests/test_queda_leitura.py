import datetime as dt

OUT = dt.date(2026, 10, 1)
NOV = dt.date(2026, 11, 1)


def test_janela_nunca_lida_devolve_none(banco):
    assert banco.controle.qtd_anterior(OUT, OUT) is None


def test_janela_iniciada_e_ainda_sem_leitura_devolve_none(banco):
    banco.controle.iniciar_janela(OUT, OUT)
    assert banco.controle.qtd_anterior(OUT, OUT) is None


def test_devolve_a_contagem_da_leitura_anterior(banco):
    c = banco.controle
    c.iniciar_janela(OUT, OUT)
    c.concluir_janela(OUT, OUT, True, 1, 10, 10, 10, 0, None)
    banco.conn.commit()
    assert c.qtd_anterior(OUT, OUT) == 10
    assert c.qtd_anterior(OUT, NOV) is None


def test_contagem_e_por_orgao(banco):
    c = banco.controle
    c.iniciar_janela(OUT, OUT)
    c.concluir_janela(OUT, OUT, True, 1, 10, 10, 10, 0, None)
    banco.conn.commit()
    assert c.para_orgao("37202").qtd_anterior(OUT, OUT) is None
