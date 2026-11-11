import json
import re

from api_simulada import RAIZ, SessaoSimulada, carregar_script
from scdp.extracao import ClienteApi

script = carregar_script("testar_janelas_api")
CASOS = json.loads((RAIZ / "2-Scripts" / "casos_janela_erro.json").read_text(encoding="utf-8"))
DATA = re.compile(r"\d{2}/\d{2}/\d{4}")


def test_formato_dos_casos():
    nomes = [c["nome"] for c in CASOS]
    assert len(nomes) == len(set(nomes))
    for c in CASOS:
        assert c["esperado"]["resultado"] in ("erro_400", "vazio"), c["nome"]
        if c["esperado"]["resultado"] == "vazio":
            assert c["esperado"]["contagem"] == 0
            for k in ("ida_de", "ida_ate", "ret_de", "ret_ate"):
                assert DATA.fullmatch(c[k]), (c["nome"], k)
        for k in ("ida_de", "ida_ate", "ret_de", "ret_ate"):
            assert k in c, (c["nome"], k)


def test_cobre_400_e_vazio():
    nomes = " ".join(c["nome"] for c in CASOS)
    for parte in ("32_dias", "2_meses", "4_meses", "ausente", "antes_de"):
        assert parte in nomes
    assert {c["esperado"]["resultado"] for c in CASOS} == {"erro_400", "vazio"}


def test_casos_contra_api_simulada(cfg):
    cli = ClienteApi(cfg, sessao=SessaoSimulada(), dormir=lambda s: None)
    resultados = script.rodar_casos(cli, CASOS)
    assert all(r["certo"] for r in resultados), [r for r in resultados if not r["certo"]]


def test_vazio_nao_e_tratado_como_erro(cfg):
    cli = ClienteApi(cfg, sessao=SessaoSimulada(), dormir=lambda s: None)
    caso = next(c for c in CASOS if c["nome"] == "ida_ate_antes_de_ida_de")
    r = script.rodar_caso(cli, caso)
    assert r["resultado"] == "vazio" and r["certo"]


def test_main_com_casos_sai_0(cfg, monkeypatch, capsys):
    monkeypatch.setattr(script.Config, "do_ambiente", classmethod(lambda c, *a: cfg))
    monkeypatch.setattr(script, "ClienteApi", lambda c: ClienteApi(c, sessao=SessaoSimulada(), dormir=lambda s: None))
    assert script.main(["--casos", str(RAIZ / "2-Scripts" / "casos_janela_erro.json")]) == 0
    saida = capsys.readouterr().out
    assert f"{len(CASOS)}/{len(CASOS)} casos conferem" in saida and cfg.chave_api not in saida
