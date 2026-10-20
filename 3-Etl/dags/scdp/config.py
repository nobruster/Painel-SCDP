from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Tuple
from urllib.parse import urlsplit

RAIZ = Path(__file__).resolve().parents[3]

OBRIGATORIAS = ("PORTAL_TRANSPARENCIA_BASE_URL", "PORTAL_TRANSPARENCIA_API_KEY", "CODIGO_ORGAO")
SCHEMA_VALIDO = re.compile(r"[a-z_][a-z0-9_]{0,62}")


class ErroConfiguracao(RuntimeError):
    pass


def carregar_env(caminho: Path) -> None:
    """Le o .env sem sobrescrever variaveis ja definidas (as do Airflow tem prioridade)."""
    if not caminho.exists():
        return
    for linha in caminho.read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if "=" in linha and not linha.startswith("#"):
            chave, valor = linha.split("=", 1)
            os.environ.setdefault(chave.strip(), valor.strip().strip("\"'"))


@dataclass(frozen=True)
class Config:
    url_base: str
    chave_api: str = field(repr=False)
    orgao: str
    schema_stg: str = "staging"
    schema_int: str = "staging"
    schema_ana: str = "staging"
    database_url: Optional[str] = field(default=None, repr=False)
    pg_host: Optional[str] = None
    pg_port: int = 5432
    pg_database: Optional[str] = None
    pg_user: Optional[str] = None
    pg_password: Optional[str] = field(default=None, repr=False)
    pg_sslmode: str = "prefer"
    meses_retorno_apos_ida: int = 12
    meses_futuros: int = 2
    meses_recentes: int = 3
    limite_dia: int = 400
    limite_noite: int = 700
    uso_do_limite: float = 0.5
    tentativas_http: int = 8
    timeout_http: int = 90
    rodadas_retentativa: int = 2
    horas_execucao_interrompida: int = 12

    def __post_init__(self) -> None:
        for schema in (self.schema_stg, self.schema_int, self.schema_ana):
            if not SCHEMA_VALIDO.fullmatch(schema):
                raise ErroConfiguracao(f"Nome de schema invalido: {schema!r}")

    def segredos(self) -> Tuple[str, ...]:
        senha_da_url = urlsplit(self.database_url).password if self.database_url else None
        return tuple(s for s in (self.chave_api, self.pg_password, senha_da_url) if s)

    def sanitizar(self, texto) -> str:
        """Troca chave da API e senhas do banco por *** antes de gravar ou logar uma mensagem de erro."""
        texto = str(texto)
        for segredo in self.segredos():
            texto = texto.replace(segredo, "***")
        return texto

    @classmethod
    def do_ambiente(cls, env_file: Optional[Path] = None) -> "Config":
        carregar_env(env_file or RAIZ / ".env")
        e = os.environ
        faltando = [k for k in OBRIGATORIAS if not e.get(k)]
        if faltando:
            raise ErroConfiguracao("Variaveis obrigatorias ausentes: " + ", ".join(faltando))
        stg = e.get("SCHEMA_STG") or "staging"
        return cls(
            url_base=e["PORTAL_TRANSPARENCIA_BASE_URL"].rstrip("/"),
            chave_api=e["PORTAL_TRANSPARENCIA_API_KEY"],
            orgao=e["CODIGO_ORGAO"],
            schema_stg=stg,
            schema_int=e.get("SCHEMA_INT") or stg,
            schema_ana=e.get("SCHEMA_ANA") or stg,
            database_url=e.get("DATABASE_URL") or None,
            pg_host=e.get("PGHOST") or None,
            pg_port=int(e.get("PGPORT") or 5432),
            pg_database=e.get("PGDATABASE") or None,
            pg_user=e.get("PGUSER") or None,
            pg_password=e.get("PGPASSWORD") or None,
            pg_sslmode=e.get("PGSSLMODE") or "prefer",
        )
