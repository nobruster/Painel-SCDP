import pytest

from api_simulada import SessaoSimulada, carregar_script
from scdp.extracao import ClienteApi, ErroPermanente

script = carregar_script("testar_janelas_api")
MARCO = ("01/03/2026", "31/03/2026", "01/03/2026", "31/03/2026")


def cliente(cfg, sessao):
    return ClienteApi(cfg, sessao=sessao, dormir=lambda s: None)


def test_conta_viagens_e_paginas(cfg):
    sessao = SessaoSimulada(padrao=32)
    assert script.contar(cliente(cfg, sessao), *MARCO) == (32, 3)
    assert [c["pagina"] for c in sessao.chamadas] == [1, 2, 3, 4]
    assert sessao.chamadas[0]["codigoOrgao"] == "33000"


def test_janela_vazia(cfg):
    assert script.contar(cliente(cfg, SessaoSimulada()), "31/03/2026", "01/03/2026", *MARCO[2:]) == (0, 0)


def test_400_vira_erro_permanente(cfg):
    with pytest.raises(ErroPermanente) as e:
        script.contar(cliente(cfg, SessaoSimulada()), "01/03/2026", "02/04/2026", *MARCO[2:])
    assert e.value.codigo == 400


def test_parametro_none_nao_e_enviado(cfg):
    sessao = SessaoSimulada()
    with pytest.raises(ErroPermanente):
        script.contar(cliente(cfg, sessao), None, *MARCO[1:])
    assert "dataIdaDe" not in sessao.chamadas[0]


def test_orgao_explicito(cfg):
    sessao = SessaoSimulada()
    assert script.contar(cliente(cfg, sessao), *MARCO, orgao="308819") == (0, 0)
    assert sessao.chamadas[0]["codigoOrgao"] == "308819"


def test_pagina_repetida_e_erro(cfg):
    class Repete(SessaoSimulada):
        def get(self, url, params=None, **kw):
            r = super().get(url, params, **kw)
            if params.get("pagina", 1) > 1:
                return type(r)(200, [{"id": 1}] * 1)
            return type(r)(200, [{"id": 1}])

    with pytest.raises(RuntimeError):
        script.contar(cliente(cfg, Repete()), *MARCO)


def test_main_janela_unica(cfg, monkeypatch, capsys):
    monkeypatch.setattr(script.Config, "do_ambiente", classmethod(lambda c, *a: cfg))
    monkeypatch.setattr(script, "ClienteApi", lambda c: cliente(c, SessaoSimulada(padrao=20)))
    args = ["--ida-de", MARCO[0], "--ida-ate", MARCO[1], "--ret-de", MARCO[2], "--ret-ate", MARCO[3]]
    assert script.main(args) == 0
    assert "viagens=20 paginas=2" in capsys.readouterr().out


def test_main_400_sai_com_1_sem_segredo(cfg, monkeypatch, capsys):
    monkeypatch.setattr(script.Config, "do_ambiente", classmethod(lambda c, *a: cfg))
    monkeypatch.setattr(script, "ClienteApi", lambda c: cliente(c, SessaoSimulada()))
    args = ["--ida-de", "01/03/2026", "--ida-ate", "02/04/2026", "--ret-de", MARCO[2], "--ret-ate", MARCO[3]]
    assert script.main(args) == 1
    saida = capsys.readouterr().out
    assert "400" in saida and cfg.chave_api not in saida
