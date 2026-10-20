import dataclasses
import os
import sys
from dataclasses import dataclass
from pathlib import Path

import pytest

TESTES = Path(__file__).resolve().parent
DAGS = TESTES.parent / "3-Etl" / "dags"
for caminho in (DAGS, TESTES):
    if str(caminho) not in sys.path:
        sys.path.insert(0, str(caminho))

from scdp import carga  # noqa: E402
from scdp.config import Config  # noqa: E402
from scdp.controle import Controle  # noqa: E402
from scdp.pipeline import Pipeline  # noqa: E402

SCHEMAS_DE_TESTE = ("zz_teste_stg", "zz_teste_int", "zz_teste_ana")


@pytest.fixture()
def cfg():
    """Schemas proprios dos testes: nunca tocam os schemas reais do banco."""
    return Config(
        url_base="https://exemplo.invalido/api-de-dados", chave_api="chave-de-teste", orgao="33000",
        schema_stg=SCHEMAS_DE_TESTE[0], schema_int=SCHEMAS_DE_TESTE[1], schema_ana=SCHEMAS_DE_TESTE[2],
    )


@dataclass
class Banco:
    cfg: Config
    conn: object
    cur: object
    controle: Controle

    def pipeline(self, extrator, dormir=lambda segundos: None) -> Pipeline:
        return Pipeline(self.cfg, self.conn, extrator, self.controle, dormir=dormir)


@pytest.fixture()
def banco(cfg):
    """PostgreSQL em TEST_DATABASE_URL (servico do CI). Cria e remove so os schemas zz_teste_*."""
    url = os.environ.get("TEST_DATABASE_URL")
    if not url:
        pytest.skip("TEST_DATABASE_URL nao definida")
    conn = carga.conectar(dataclasses.replace(cfg, database_url=url))
    cur = conn.cursor()

    def recriar(criar: bool):
        for s in SCHEMAS_DE_TESTE:
            cur.execute(f"DROP SCHEMA IF EXISTS {s} CASCADE")
            if criar:
                cur.execute(f"CREATE SCHEMA {s}")
        conn.commit()

    recriar(True)
    carga.aplicar_schema(cur)
    conn.commit()
    yield Banco(cfg, conn, cur, Controle(cur, conn, cfg.orgao, sanitizar=cfg.sanitizar))
    if not conn.closed:
        conn.rollback()
        conn.close()
    limpeza = carga.conectar(dataclasses.replace(cfg, database_url=url))
    cur2 = limpeza.cursor()
    for s in SCHEMAS_DE_TESTE:
        cur2.execute(f"DROP SCHEMA IF EXISTS {s} CASCADE")
    limpeza.commit()
    limpeza.close()
