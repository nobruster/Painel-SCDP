import dataclasses
import os

import pytest

from scdp.config import Config, ErroConfiguracao


def test_nome_de_schema_e_validado(cfg):
    for ruim in ("x; DROP TABLE y", "Staging", "a b", "1abc", "", "a-b", "x" * 64):
        with pytest.raises(ErroConfiguracao):
            dataclasses.replace(cfg, schema_stg=ruim)
    dataclasses.replace(cfg, schema_stg="staging_2")


def test_schemas_reservados_e_do_sistema_sao_recusados(cfg):
    for ruim in ("pg_catalog", "pg_temp", "user", "select"):
        with pytest.raises(ErroConfiguracao):
            dataclasses.replace(cfg, schema_ana=ruim)


def test_database_url_invalida_nao_vaza_a_senha_na_mensagem(cfg):
    with pytest.raises(ErroConfiguracao) as e:
        dataclasses.replace(cfg, database_url="password=a b")
    assert "a b" not in str(e.value)


def test_url_da_api_precisa_ser_https(cfg):
    with pytest.raises(ErroConfiguracao):
        dataclasses.replace(cfg, url_base="http://api.exemplo/api-de-dados")


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


def test_sanitizar_com_senha_curta_dentro_da_chave_nao_deixa_resto_da_chave(cfg):
    c = dataclasses.replace(cfg, chave_api="abc123XYZ", pg_password="a")
    msg = c.sanitizar("erro com abc123XYZ no cabecalho")
    assert "123XYZ" not in msg and "XYZ" not in msg


def test_sanitizar_senha_com_percent_encoding_e_formato_chave_valor(cfg):
    c = dataclasses.replace(cfg, database_url="postgresql://u:p%40ss%3Aword@h/db")
    msg = c.sanitizar("falha: p%40ss%3Aword e tambem p@ss:word")
    assert "p%40ss" not in msg and "p@ss:word" not in msg
    c2 = dataclasses.replace(cfg, database_url="host=h dbname=d user=u password=segredo-kv")
    assert "segredo-kv" not in c2.sanitizar("conexao falhou com segredo-kv")


def test_variaveis_obrigatorias(tmp_path, monkeypatch):
    monkeypatch.setattr(os, "environ", {})
    with pytest.raises(ErroConfiguracao):
        Config.do_ambiente(tmp_path / "nao_existe.env")


def test_porta_invalida(tmp_path, monkeypatch):
    monkeypatch.setattr(os, "environ", {"PORTAL_TRANSPARENCIA_BASE_URL": "https://x/api", "PORTAL_TRANSPARENCIA_API_KEY": "k",
                                        "CODIGO_ORGAO": "1", "PGPORT": "abc"})
    with pytest.raises(ErroConfiguracao):
        Config.do_ambiente(tmp_path / "nao_existe.env")


def test_env_do_processo_tem_prioridade_sobre_o_arquivo(tmp_path, monkeypatch):
    arquivo = tmp_path / ".env"
    arquivo.write_text("PORTAL_TRANSPARENCIA_BASE_URL=https://arquivo/api\nPORTAL_TRANSPARENCIA_API_KEY=do-arquivo\nCODIGO_ORGAO=1\n",
                       encoding="utf-8")
    monkeypatch.setattr(os, "environ", {"PORTAL_TRANSPARENCIA_API_KEY": "do-processo"})
    c = Config.do_ambiente(arquivo)
    assert c.chave_api == "do-processo"
    assert c.url_base == "https://arquivo/api"
