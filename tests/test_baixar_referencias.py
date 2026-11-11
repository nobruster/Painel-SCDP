import pytest

from api_simulada import Resposta, carregar_script
from scdp.extracao import ClienteApi, ErroPermanente

script = carregar_script("baixar_referencias")


class SessaoOrgaos:
    def __init__(self, status_spec=200):
        self.headers = {}
        self.urls = []
        self.status_spec = status_spec
        self.orgaos = {
            "orgaos-siafi": [{"codigo": "33000", "descricao": "Ministério da Previdência Social"},
                             {"codigo": "00000", "descricao": "CODIGO INVALIDO; X"}],
            "orgaos-siape": [{"codigo": "00001", "descricao": "IGNORADO"}],
        }

    def get(self, url, params=None, timeout=None, allow_redirects=True):
        self.urls.append(url)
        if url.endswith("/v3/api-docs"):
            if self.status_spec != 200:
                return Resposta(self.status_spec, "falhou")
            return Resposta(200, {"paths": {"/a": {}, "/b": {}}})
        lista = self.orgaos[url.rsplit("/", 1)[1]]
        pagina = params["pagina"]
        return Resposta(200, lista if pagina == 1 else [])


def cliente(cfg, sessao):
    return ClienteApi(cfg, sessao=sessao, dormir=lambda s: None)


def test_url_da_spec_usa_o_host_da_api(cfg):
    assert script.url_spec(cfg) == "https://exemplo.invalido/v3/api-docs"


def test_listar_orgaos_ordena_e_deduplica(cfg):
    s = SessaoOrgaos()
    s.orgaos["orgaos-siafi"].append({"codigo": "33000", "descricao": "Ministério da Previdência Social"})
    r = script.listar_orgaos(cliente(cfg, s), "orgaos-siafi")
    assert [o["codigo"] for o in r] == ["00000", "33000"]


def test_csv_no_formato_atual():
    b = script.para_csv([{"codigo": "00000", "descricao": "A; B"}, {"codigo": "33000", "descricao": "Previdência"}])
    assert b.startswith("﻿codigo;descricao\r\n".encode("utf-8"))
    assert b.endswith(b"\r\n") and "33000;Previdência".encode("utf-8") in b and b"A, B" in b


def test_dry_run_nao_grava(cfg, tmp_path):
    saida = []
    destino, spec = tmp_path / "ref", tmp_path / "saidas" / "api-docs.json"
    script.baixar(cliente(cfg, SessaoOrgaos()), destino, spec, True, saida.append)
    assert not destino.exists() and not spec.exists()
    assert any("2 caminhos" in s and "dry-run" in s for s in saida)
    assert any("orgaos_siafi.csv: 2 orgaos" in s for s in saida)


def test_grava_listas_e_spec(cfg, tmp_path):
    destino, spec = tmp_path / "ref", tmp_path / "saidas" / "api-docs.json"
    assert script.baixar(cliente(cfg, SessaoOrgaos()), destino, spec, False, lambda s: None) == 0
    assert (destino / "orgaos_siape.csv").read_bytes().startswith("﻿codigo;descricao".encode("utf-8"))
    assert "33000;Ministério".encode("utf-8") in (destino / "orgaos_siafi.csv").read_bytes()
    assert spec.exists()


def test_lista_vazia_nao_sobrescreve(cfg, tmp_path):
    s = SessaoOrgaos()
    s.orgaos["orgaos-siafi"] = []
    destino = tmp_path / "ref"
    with pytest.raises(RuntimeError):
        script.baixar(cliente(cfg, s), destino, tmp_path / "s.json", False, lambda x: None)
    assert not (destino / "orgaos_siafi.csv").exists()


def test_main_erro_permanente_sai_1_sem_segredo(cfg, monkeypatch, capsys, tmp_path):
    monkeypatch.setattr(script.Config, "do_ambiente", classmethod(lambda c, *a: cfg))
    monkeypatch.setattr(script, "ClienteApi", lambda c: cliente(c, SessaoOrgaos(status_spec=401)))
    assert script.main(["--dry-run", "--destino", str(tmp_path)]) == 1
    saida = capsys.readouterr().out
    assert "401" in saida and cfg.chave_api not in saida


def test_main_dry_run_sai_0(cfg, monkeypatch, capsys, tmp_path):
    monkeypatch.setattr(script.Config, "do_ambiente", classmethod(lambda c, *a: cfg))
    monkeypatch.setattr(script, "ClienteApi", lambda c: cliente(c, SessaoOrgaos()))
    assert script.main(["--dry-run", "--destino", str(tmp_path / "x")]) == 0
    assert not (tmp_path / "x").exists()
