"""Teste de integração: precisa de um PostgreSQL vazio em TEST_DATABASE_URL (no CI, o serviço do workflow).
Nunca aponte para o banco real: o teste grava dados fictícios."""
import copy
import datetime as dt
import os

import psycopg2
import pytest

URL = os.environ.get("TEST_DATABASE_URL")
pytestmark = pytest.mark.skipif(not URL, reason="TEST_DATABASE_URL não definida")


def viagem(vid, inicio, fim, total, passagem, diarias, outros=0.0, orgao="33000"):
    return {
        "id": vid,
        "viagem": {"pcdp": f"{vid:019d}", "numPcdp": f"{vid % 1000:06d}/26", "ano": 2026,
                   "urgenciaViagem": "Não", "motivo": "texto livre que não deve ir para a analítica"},
        "situacao": "Realizada", "tipoViagem": "Nacional",
        "beneficiario": {"nome": f"PESSOA {vid}", "cpfFormatado": "***.123.456-**"},
        "orgao": {"codigoSIAFI": orgao, "nome": "Ministério de Teste", "sigla": "MT",
                  "orgaoMaximo": {"sigla": "MT"}},
        "unidadeGestoraResponsavel": {"codigo": "330094", "nome": "UG TESTE"},
        "dataInicioAfastamento": inicio, "dataFimAfastamento": fim,
        "valorTotalViagem": total, "valorTotalPassagem": passagem, "valorTotalDiarias": diarias,
        "valorTotalTaxaAgenciamento": 0.0, "valorTotalRestituicao": 0.0,
        "valorTotalDevolucao": 0.0, "valorMulta": 0.0,
    }


@pytest.fixture()
def banco(carga):
    conn = psycopg2.connect(URL, cursor_factory=carga.Cursor)
    cur = conn.cursor()
    for s in ("staging", "intermediaria", "analitica"):
        cur.execute(f"DROP SCHEMA IF EXISTS {s} CASCADE")
        cur.execute(f"CREATE SCHEMA {s}")
    conn.commit()
    schema = open(carga.os.path.join(carga.HERE, "sql", "schema.sql"), encoding="utf-8").read()
    cur.execute(schema)
    conn.commit()
    yield conn, cur
    conn.close()


def test_carga_incremental_ponta_a_ponta(carga, banco, monkeypatch):
    conn, cur = banco
    ida, ret = dt.date(2026, 8, 1), dt.date(2026, 8, 1)
    dados = [
        viagem(1, "2026-08-03", "2026-08-04", 1000.0, 600.0, 400.0),
        viagem(2, "2026-08-10", "2026-08-12", 1500.0, 500.0, 900.0, outros=100.0),
        viagem(3, "2026-08-20", "2026-08-21", 300.0, 0.0, 300.0),
    ]
    monkeypatch.setattr(carga, "buscar", lambda i, r: (copy.deepcopy(dados), 1))

    ok, qtd, novos, alterados, aviso = carga.processar(cur, conn, ida, ret, None)
    assert (ok, qtd, novos, alterados) == (True, 3, 3, 0)

    ok, qtd, novos, alterados, aviso = carga.processar(cur, conn, ida, ret, {"status": "OK", "qtd_api": 3, "fim": None})
    assert (ok, novos, alterados) == (True, 0, 0)

    dados[0]["valorTotalViagem"] = 1100.0
    dados[0]["valorTotalPassagem"] = 700.0
    ok, _, novos, alterados, _ = carga.processar(cur, conn, ida, ret, {"status": "OK", "qtd_api": 3, "fim": None})
    assert (ok, novos, alterados) == (True, 0, 1)

    dados.append(viagem(4, "2026-08-25", "2026-08-26", 200.0, 0.0, 200.0))
    ok, _, novos, alterados, _ = carga.processar(cur, conn, ida, ret, {"status": "OK", "qtd_api": 3, "fim": None})
    assert (ok, novos, alterados) == (True, 1, 0)

    cur.execute("SELECT count(*) FROM staging.stg_viagem")
    assert cur.fetchone()[0] == 4
    cur.execute("SELECT count(*) FROM intermediaria.int_viagem")
    assert cur.fetchone()[0] == 4
    cur.execute("SELECT valor_outros_gastos, dias_afastamento FROM intermediaria.int_viagem WHERE id = 2")
    assert cur.fetchone() == (100.0, 3)

    processadas = carga.atualizar_analitica(cur)
    conn.commit()
    assert processadas == 4
    for tabela in ("fct_viagem", "obt_viagem"):
        cur.execute(f"SELECT count(*) FROM analitica.{tabela}")
        assert cur.fetchone()[0] == 4
        cur.execute(
            "SELECT 1 FROM information_schema.columns WHERE table_schema='analitica' AND table_name=%s AND column_name='motivo'",
            (tabela,))
        assert cur.fetchone() is None, "motivo não pode estar na analítica"
    cur.execute("SELECT valor_total_viagem FROM analitica.obt_viagem WHERE viagem_id = 1")
    assert float(cur.fetchone()[0]) == 1100.0
    cur.execute("SELECT count(*) FROM analitica.dim_orgao")
    assert cur.fetchone()[0] == 1

    # sem mudança: a analítica só reprocessa a viagem da marca d'água
    assert carga.atualizar_analitica(cur) <= 1
    conn.commit()

    # mudança de nome do órgão propaga para as linhas da obt
    cur.execute("UPDATE intermediaria.int_viagem SET orgao_nome = 'Nome Novo', atualizado_em = now() WHERE id = 1")
    conn.commit()
    carga.atualizar_analitica(cur)
    conn.commit()
    cur.execute("SELECT DISTINCT orgao_nome FROM analitica.obt_viagem")
    assert cur.fetchall() == [("Nome Novo",)]

    cur.execute("SELECT status, qtd_api, qtd_carregada FROM staging.ctl_janela")
    assert cur.fetchone() == ("OK", 4, 4)
