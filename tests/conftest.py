import importlib.util
import os
from pathlib import Path

import pytest

os.environ.setdefault("PORTAL_TRANSPARENCIA_BASE_URL", "https://exemplo.invalido/api-de-dados")
os.environ.setdefault("PORTAL_TRANSPARENCIA_API_KEY", "chave-de-teste")
os.environ.setdefault("CODIGO_ORGAO", "33000")
os.environ["SCHEMA_STG"] = "staging"
os.environ["SCHEMA_INT"] = "intermediaria"
os.environ["SCHEMA_ANA"] = "analitica"

RAIZ = Path(__file__).resolve().parent.parent
CARGA = RAIZ / "3-Etl" / "dags" / "carga_viagens.py"


@pytest.fixture(scope="session")
def carga():
    spec = importlib.util.spec_from_file_location("carga_viagens", CARGA)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo
