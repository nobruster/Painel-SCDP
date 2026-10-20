import dataclasses

import pytest

from scdp.config import Config, ErroConfiguracao


def test_nome_de_schema_e_validado(cfg):
    for ruim in ("x; DROP TABLE y", "Staging", "a b", "1abc", "", "a-b", "x" * 64):
        with pytest.raises(ErroConfiguracao):
            dataclasses.replace(cfg, schema_stg=ruim)
    dataclasses.replace(cfg, schema_stg="staging_2")


def test_repr_nao_mostra_segredos(cfg):
    c = dataclasses.replace(cfg, pg_password="s3nha-secreta", database_url="postgresql://u:s3nha-url@h/db")
    texto = repr(c)
    assert "chave-de-teste" not in texto
    assert "s3nha-secreta" not in texto
    assert "s3nha-url" not in texto


def test_sanitizar_troca_chave_e_senhas(cfg):
    c = dataclasses.replace(cfg, pg_password="s3nha-secreta", database_url="postgresql://u:s3nha-url@h/db")
    msg = c.sanitizar("falha com chave-de-teste e s3nha-secreta e s3nha-url na conexao")
    assert "chave-de-teste" not in msg and "s3nha-secreta" not in msg and "s3nha-url" not in msg
    assert msg.count("***") == 3


def test_variaveis_obrigatorias(tmp_path, monkeypatch):
    for k in ("PORTAL_TRANSPARENCIA_BASE_URL", "PORTAL_TRANSPARENCIA_API_KEY", "CODIGO_ORGAO"):
        monkeypatch.delenv(k, raising=False)
    with pytest.raises(ErroConfiguracao):
        Config.do_ambiente(tmp_path / "nao_existe.env")


def test_env_do_processo_tem_prioridade_sobre_o_arquivo(tmp_path, monkeypatch):
    arquivo = tmp_path / ".env"
    arquivo.write_text("PORTAL_TRANSPARENCIA_BASE_URL=https://arquivo/api\nPORTAL_TRANSPARENCIA_API_KEY=do-arquivo\nCODIGO_ORGAO=1\n",
                       encoding="utf-8")
    monkeypatch.setenv("PORTAL_TRANSPARENCIA_API_KEY", "do-processo")
    monkeypatch.delenv("PORTAL_TRANSPARENCIA_BASE_URL", raising=False)
    monkeypatch.delenv("CODIGO_ORGAO", raising=False)
    c = Config.do_ambiente(arquivo)
    assert c.chave_api == "do-processo"
    assert c.url_base == "https://arquivo/api"
