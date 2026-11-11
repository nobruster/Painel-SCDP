import os

import pytest

from scdp.config import Config, ErroConfiguracao, parse_orgaos


def ambiente(monkeypatch, codigo):
    monkeypatch.setattr(os, "environ", {"PORTAL_TRANSPARENCIA_BASE_URL": "https://x/api", "PORTAL_TRANSPARENCIA_API_KEY": "k",
                                        "CODIGO_ORGAO": codigo})


def test_um_codigo_mantem_o_comportamento(tmp_path, monkeypatch):
    ambiente(monkeypatch, "33000")
    c = Config.do_ambiente(tmp_path / "nao_existe.env")
    assert c.orgao == "33000"
    assert c.orgaos == ("33000",)


def test_lista_de_codigos(tmp_path, monkeypatch):
    ambiente(monkeypatch, "33000, 37202 ,33206")
    c = Config.do_ambiente(tmp_path / "nao_existe.env")
    assert c.orgaos == ("33000", "37202", "33206")


def test_codigo_repetido_conta_uma_vez():
    assert parse_orgaos("33000,33000,37202") == ("33000", "37202")


@pytest.mark.parametrize("ruim", ["1", "330000", "abcde", "33000,", "33000,,37202", "33000;37202", "", "308819"])
def test_codigo_invalido_levanta_erro(tmp_path, monkeypatch, ruim):
    ambiente(monkeypatch, ruim or " ")
    with pytest.raises(ErroConfiguracao):
        Config.do_ambiente(tmp_path / "nao_existe.env")
