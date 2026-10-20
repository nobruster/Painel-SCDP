"""Descricao segura de excecoes: sem segredos e sem dados pessoais que o PostgreSQL coloca no DETAIL ou no valor ofensivo."""
from __future__ import annotations

import re

import psycopg2

from .config import Config

_CORTE_VALOR = re.compile(r"""\s*:\s*["'(]|["']""")


def _sem_valor(mensagem: str) -> str:
    """'invalid input syntax for type bigint: "FULANO"' -> 'invalid input syntax for type bigint'."""
    return _CORTE_VALOR.split(mensagem, maxsplit=1)[0].strip()


def descrever(cfg: Config, erro: BaseException) -> str:
    if isinstance(erro, psycopg2.Error):
        diag = getattr(erro, "diag", None)
        principal = getattr(diag, "message_primary", None) or (str(erro).splitlines() or [""])[0]
        return cfg.sanitizar(f"{type(erro).__name__}[{erro.pgcode}]: {_sem_valor(principal)}")
    return cfg.sanitizar(erro)
