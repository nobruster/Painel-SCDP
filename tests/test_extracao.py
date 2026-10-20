import datetime as dt

import pytest
import requests

from scdp.extracao import BRASILIA, ClienteApi, ErroPermanente

IDA = RET = dt.date(2026, 3, 1)


class Resposta:
    def __init__(self, status, dados=None, headers=None, texto=""):
        self.status_code = status
        self._dados = dados if dados is not None else []
        self.headers = headers or {}
        self.text = texto

    def json(self):
        return self._dados


class Sessao:
    def __init__(self, respostas):
        self.headers = {}
        self.respostas = list(respostas)
        self.params = []

    def get(self, url, params, timeout, **kw):
        self.kw = kw
        self.params.append(params)
        r = self.respostas.pop(0)
        if isinstance(r, Exception):
            raise r
        return r


def cliente(cfg, respostas, hora=10):
    esperas = []
    sessao = Sessao(respostas)
    c = ClienteApi(cfg, sessao=sessao, dormir=esperas.append,
                   agora=lambda: dt.datetime(2026, 10, 19, hora, 0, tzinfo=BRASILIA))
    return c, sessao, esperas


def test_pagina_ate_vir_lista_vazia_e_monta_as_datas(cfg):
    c, sessao, _ = cliente(cfg, [Resposta(200, [{"id": 1}]), Resposta(200, [{"id": 2}]), Resposta(200, [])])
    registros, paginas = c.buscar(IDA, RET)
    assert registros == [{"id": 1}, {"id": 2}]
    assert paginas == 2
    assert [p["pagina"] for p in sessao.params] == [1, 2, 3]
    assert sessao.params[0]["dataIdaDe"] == "01/03/2026" and sessao.params[0]["dataRetornoAte"] == "31/03/2026"
    assert sessao.params[0]["codigoOrgao"] == "33000"
    assert sessao.headers["chave-api-dados"] == "chave-de-teste"


def test_erro_400_e_401_sao_permanentes(cfg):
    for codigo in (400, 401):
        c, _, _ = cliente(cfg, [Resposta(codigo, texto="detalhe")])
        with pytest.raises(ErroPermanente) as e:
            c.buscar(IDA, RET)
        assert e.value.codigo == codigo


def test_504_e_repetido_com_espera_crescente(cfg):
    c, _, esperas = cliente(cfg, [Resposta(504), Resposta(504), Resposta(200, [{"id": 1}]), Resposta(200, [])])
    registros, _ = c.buscar(IDA, RET)
    assert registros == [{"id": 1}]
    assert esperas[:2] == [4, 8]


def test_429_espera_o_retry_after(cfg):
    c, _, esperas = cliente(cfg, [Resposta(429, headers={"Retry-After": "7"}), Resposta(200, [])])
    c.buscar(IDA, RET)
    assert esperas[0] == 7


def test_queda_de_rede_e_repetida(cfg):
    c, _, _ = cliente(cfg, [requests.ConnectionError("caiu"), Resposta(200, [])])
    assert c.buscar(IDA, RET) == ([], 0)


def test_esgota_as_tentativas(cfg):
    c, _, _ = cliente(cfg, [Resposta(503)] * cfg.tentativas_http)
    with pytest.raises(RuntimeError):
        c.buscar(IDA, RET)


def test_resposta_200_que_nao_e_json_e_repetida(cfg):
    class SemJson(Resposta):
        def json(self):
            raise ValueError("nao e json")

    c, _, esperas = cliente(cfg, [SemJson(200), Resposta(200, [{"id": 1}]), Resposta(200, [])])
    assert c.buscar(IDA, RET)[0] == [{"id": 1}]
    assert esperas[0] == 4


def test_retry_after_em_formato_de_data_usa_o_padrao(cfg):
    c, _, esperas = cliente(cfg, [Resposta(429, headers={"Retry-After": "Wed, 21 Oct 2026 07:28:00 GMT"}), Resposta(200, [])])
    c.buscar(IDA, RET)
    assert esperas[0] == 60


def test_retry_after_tem_teto(cfg):
    c, _, esperas = cliente(cfg, [Resposta(429, headers={"Retry-After": "99999"}), Resposta(200, [])])
    c.buscar(IDA, RET)
    assert esperas[0] == 300


@pytest.mark.parametrize("codigo", [403, 404])
def test_403_e_404_tambem_sao_permanentes(cfg, codigo):
    c, sessao, _ = cliente(cfg, [Resposta(codigo)])
    with pytest.raises(ErroPermanente) as e:
        c.buscar(IDA, RET)
    assert e.value.codigo == codigo
    assert len(sessao.params) == 1


def test_corpo_de_erro_que_ecoa_a_chave_e_mascarado(cfg):
    c, _, _ = cliente(cfg, [Resposta(401, texto="chave invalida: chave-de-teste")])
    with pytest.raises(ErroPermanente) as e:
        c.buscar(IDA, RET)
    assert "chave-de-teste" not in str(e.value)


def test_nao_segue_redirecionamento_para_nao_vazar_a_chave(cfg):
    c, sessao, _ = cliente(cfg, [Resposta(200, [])])
    c.buscar(IDA, RET)
    assert sessao.kw["allow_redirects"] is False
    c2, _, _ = cliente(cfg, [Resposta(302, texto="Location: http://outro-host")])
    with pytest.raises(ErroPermanente) as e:
        c2.buscar(IDA, RET)
    assert e.value.codigo == 302


def test_chave_cortada_pelo_limite_de_150_caracteres_nao_vaza(cfg):
    texto = "x" * 145 + "chave-de-teste"
    c, _, _ = cliente(cfg, [Resposta(400, texto=texto)])
    with pytest.raises(ErroPermanente) as e:
        c.buscar(IDA, RET)
    assert "chave" not in str(e.value).replace("chave invalida", "")
    assert "***" in str(e.value)


def test_resposta_que_nao_e_lista_nao_vira_dado(cfg):
    import dataclasses
    curto = dataclasses.replace(cfg, tentativas_http=2)
    c, _, _ = cliente(curto, [Resposta(200, {"mensagem": "manutencao"}), Resposta(200, {"mensagem": "manutencao"})])
    with pytest.raises(RuntimeError):
        c.buscar(IDA, RET)


def test_pagina_repetida_nao_gera_loop_infinito(cfg):
    pagina = [{"id": 1}, {"id": 2}]
    c, sessao, _ = cliente(cfg, [Resposta(200, pagina), Resposta(200, pagina), Resposta(200, pagina)])
    with pytest.raises(RuntimeError, match="de novo"):
        c.buscar(IDA, RET)
    assert len(sessao.params) == 2


def test_limite_de_paginas(cfg, monkeypatch):
    from scdp import extracao
    monkeypatch.setattr(extracao, "MAX_PAGINAS", 3)
    c, _, _ = cliente(cfg, [Resposta(200, [{"id": n}]) for n in range(10)])
    with pytest.raises(RuntimeError, match="paginas"):
        c.buscar(IDA, RET)


def test_pausa_segue_o_limite_do_horario_de_brasilia(cfg):
    c, _, esperas = cliente(cfg, [], hora=3)
    c.pausar()
    c2, _, esperas2 = cliente(cfg, [], hora=10)
    c2.pausar()
    assert esperas == [60 / (cfg.limite_noite * cfg.uso_do_limite)]
    assert esperas2 == [60 / (cfg.limite_dia * cfg.uso_do_limite)]
