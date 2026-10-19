import datetime as dt
from collections import Counter


def test_faixa_meses_de_30_31_e_fevereiro(carga):
    assert carga.faixa(dt.date(2026, 3, 1)) == ("01/03/2026", "31/03/2026")
    assert carga.faixa(dt.date(2026, 4, 1)) == ("01/04/2026", "30/04/2026")
    assert carga.faixa(dt.date(2026, 2, 1)) == ("01/02/2026", "28/02/2026")
    assert carga.faixa(dt.date(2028, 2, 1)) == ("01/02/2028", "29/02/2028")


def test_add_meses_virada_de_ano(carga):
    assert carga.add_meses(dt.date(2026, 11, 1), 3) == dt.date(2027, 2, 1)
    assert carga.add_meses(dt.date(2026, 1, 1), -1) == dt.date(2025, 12, 1)


def test_planejamento_cobre_dentro_do_mes_virada_e_longas(carga):
    hoje = dt.date(2026, 10, 19)
    janelas = list(carga.planejar(dt.date(2025, 1, 1), hoje))
    distancias = Counter((r.year - i.year) * 12 + r.month - i.month for i, r in janelas)
    assert sorted(distancias) == list(range(0, 13))
    assert set(distancias.values()) == {24}
    assert len(janelas) == 312
    assert not any(r < i for i, r in janelas)


def test_planejamento_inclui_meses_futuros(carga):
    hoje = dt.date(2026, 10, 19)
    idas = {i for i, _ in carga.planejar(dt.date(2026, 8, 1), hoje)}
    assert max(idas) == dt.date(2026, 12, 1)


def test_modo_diario_le_so_janelas_recentes_e_pendentes(carga):
    hoje = dt.date(2026, 10, 19)
    ok = {"status": "OK", "qtd_api": 0, "fim": None}
    antiga = (dt.date(2026, 2, 1), dt.date(2026, 2, 1))
    recente = (dt.date(2026, 9, 1), dt.date(2026, 9, 1))
    longa_antiga_termina_agora = (dt.date(2026, 2, 1), dt.date(2026, 9, 1))
    assert not carga.precisa_ler(ok, *antiga, hoje, "diario")
    assert carga.precisa_ler(ok, *recente, hoje, "diario")
    assert carga.precisa_ler(ok, *longa_antiga_termina_agora, hoje, "diario")
    assert carga.precisa_ler(None, *antiga, hoje, "diario")
    assert carga.precisa_ler({"status": "ERRO", "qtd_api": 1, "fim": None}, *antiga, hoje, "diario")


def test_modo_completo_le_tudo(carga):
    hoje = dt.date(2026, 10, 19)
    ok = {"status": "OK", "qtd_api": 0, "fim": None}
    assert carga.precisa_ler(ok, dt.date(2025, 1, 1), dt.date(2025, 1, 1), hoje, "completo")


def test_hash_nao_depende_da_ordem_das_chaves(carga):
    a = {"id": 1, "valor": 10, "x": {"b": 1, "a": 2}}
    b = {"x": {"a": 2, "b": 1}, "valor": 10, "id": 1}
    assert carga.hash_de(a) == carga.hash_de(b)
    assert carga.hash_de(a) != carga.hash_de({**a, "valor": 11})
