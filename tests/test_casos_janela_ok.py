import datetime as dt
import json
import re

import pytest

from api_simulada import RAIZ, SessaoSimulada, carregar_script
from scdp.extracao import ClienteApi

script = carregar_script("testar_janelas_api")
CASOS = json.loads((RAIZ / "2-Scripts" / "casos_janela_ok.json").read_text(encoding="utf-8"))
DATA = re.compile(r"\d{2}/\d{2}/\d{4}")


def test_formato_dos_casos():
    nomes = [c["nome"] for c in CASOS]
    assert len(nomes) == len(set(nomes))
    for c in CASOS:
        for k in ("ida_de", "ida_ate", "ret_de", "ret_ate"):
            assert DATA.fullmatch(c[k]), (c["nome"], k)
        assert c["esperado"]["resultado"] == "ok"
        assert c["esperado"].get("contagem") is None or c["esperado"]["contagem"] >= 0


def test_cobre_os_tipos_de_janela():
    nomes = " ".join(c["nome"] for c in CASOS)
    for parte in ("mes_0", "mes_mais_1", "mes_mais_3", "mes_mais_12", "dia_unico", "semana", "limite_31"):
        assert parte in nomes


def test_nao_ha_segredo_no_arquivo():
    texto = (RAIZ / "2-Scripts" / "casos_janela_ok.json").read_text(encoding="utf-8")
    assert "chave" not in texto.lower()


def test_janelas_dentro_do_limite_de_um_mes():
    for c in CASOS:
        for de, ate in ((c["ida_de"], c["ida_ate"]), (c["ret_de"], c["ret_ate"])):
            d = dt.datetime.strptime(de, "%d/%m/%Y").date()
            a = dt.datetime.strptime(ate, "%d/%m/%Y").date()
            assert 0 <= (a - d).days <= 31, c["nome"]


def test_casos_contra_api_simulada(cfg):
    contagens = {(c["ida_de"], c["ida_ate"], c["ret_de"], c["ret_ate"]): c["esperado"]["contagem"]
                 for c in CASOS if c["esperado"].get("contagem") is not None}
    cli = ClienteApi(cfg, sessao=SessaoSimulada(contagens=contagens), dormir=lambda s: None)
    resultados = script.rodar_casos(cli, CASOS)
    assert all(r["certo"] for r in resultados), [r for r in resultados if not r["certo"]]
    por_nome = {r["nome"]: r for r in resultados}
    assert por_nome["mes_0_agosto_2026"]["contagem"] == 142 and por_nome["mes_0_agosto_2026"]["paginas"] == 10


def test_caso_divergente_e_detectado(cfg):
    cli = ClienteApi(cfg, sessao=SessaoSimulada(padrao=5), dormir=lambda s: None)
    r = script.rodar_caso(cli, CASOS[0])
    assert not r["certo"] and r["contagem"] == 5
