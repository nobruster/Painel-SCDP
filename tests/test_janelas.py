import datetime as dt
from collections import Counter

from scdp import janelas

HOJE = dt.date(2026, 10, 19)
OK = {"status": "OK", "qtd_api": 0, "fim": None}


def test_faixa_meses_de_30_31_e_fevereiro():
    assert janelas.faixa(dt.date(2026, 3, 1)) == ("01/03/2026", "31/03/2026")
    assert janelas.faixa(dt.date(2026, 4, 1)) == ("01/04/2026", "30/04/2026")
    assert janelas.faixa(dt.date(2026, 2, 1)) == ("01/02/2026", "28/02/2026")
    assert janelas.faixa(dt.date(2028, 2, 1)) == ("01/02/2028", "29/02/2028")


def test_add_meses_virada_de_ano():
    assert janelas.add_meses(dt.date(2026, 11, 1), 3) == dt.date(2027, 2, 1)
    assert janelas.add_meses(dt.date(2026, 1, 1), -1) == dt.date(2025, 12, 1)


def test_planejamento_cobre_dentro_do_mes_virada_e_longas(cfg):
    todas = list(janelas.planejar(dt.date(2025, 1, 1), HOJE, cfg))
    distancias = Counter((r.year - i.year) * 12 + r.month - i.month for i, r in todas)
    assert sorted(distancias) == list(range(0, 13))
    assert set(distancias.values()) == {24}
    assert len(todas) == 312
    assert not any(r < i for i, r in todas)


def test_planejamento_inclui_meses_futuros(cfg):
    idas = {i for i, _ in janelas.planejar(dt.date(2026, 8, 1), HOJE, cfg)}
    assert max(idas) == dt.date(2026, 12, 1)


def test_modo_diario_le_so_janelas_recentes_e_pendentes(cfg):
    antiga = (dt.date(2026, 2, 1), dt.date(2026, 2, 1))
    recente = (dt.date(2026, 9, 1), dt.date(2026, 9, 1))
    longa_antiga_termina_agora = (dt.date(2026, 2, 1), dt.date(2026, 9, 1))
    assert not janelas.precisa_ler(OK, *antiga, HOJE, "diario", cfg)
    assert janelas.precisa_ler(OK, *recente, HOJE, "diario", cfg)
    assert janelas.precisa_ler(OK, *longa_antiga_termina_agora, HOJE, "diario", cfg)
    assert janelas.precisa_ler(None, *antiga, HOJE, "diario", cfg)
    assert janelas.precisa_ler({"status": "ERRO", "qtd_api": 1, "fim": None}, *antiga, HOJE, "diario", cfg)


def test_modo_completo_le_tudo(cfg):
    assert janelas.precisa_ler(OK, dt.date(2025, 1, 1), dt.date(2025, 1, 1), HOJE, "completo", cfg)


def test_retomada_poe_janelas_pendentes_primeiro():
    a, b, c, d = (dt.date(2026, m, 1) for m in (1, 2, 3, 4))
    estados = {
        (a, a): {"status": "OK", "qtd_api": 1, "fim": None},
        (b, b): {"status": "ERRO", "qtd_api": None, "fim": None},
        (c, c): {"status": "EXECUTANDO", "qtd_api": None, "fim": None},
    }
    ordem = janelas.ordenar_janelas([(a, a), (b, b), (c, c), (d, d)], estados)
    assert ordem[:2] == [(b, b), (c, c)]
    assert ordem[2:] == [(a, a), (d, d)]
