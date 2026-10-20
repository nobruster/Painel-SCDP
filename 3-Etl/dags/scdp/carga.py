"""Carga: tudo que escreve ou le a camada staging e a conexao com o PostgreSQL."""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Dict, Optional, Sequence

import psycopg2
from psycopg2.extras import Json, execute_values

from .config import Config, ErroConfiguracao

SCHEMA_SQL = Path(__file__).resolve().parent.parent / "sql" / "schema.sql"

UPSERT_STAGING = (
    "INSERT INTO @STG@.stg_viagem (id, janela_ida, janela_retorno, payload, hash_registro) VALUES %s "
    "ON CONFLICT (id) DO UPDATE SET janela_ida = EXCLUDED.janela_ida, janela_retorno = EXCLUDED.janela_retorno, "
    "payload = EXCLUDED.payload, hash_registro = EXCLUDED.hash_registro, atualizado_em = now()"
)

KEEPALIVES = dict(keepalives=1, keepalives_idle=60, keepalives_interval=10, keepalives_count=3)


def criar_classe_cursor(cfg: Config):
    """Cursor que troca @STG@, @INT@ e @ANA@ pelos schemas configurados, so nos textos de SQL (nunca nos dados)."""
    trocas = (("@STG@", cfg.schema_stg), ("@INT@", cfg.schema_int), ("@ANA@", cfg.schema_ana))

    class CursorComSchemas(psycopg2.extensions.cursor):
        @staticmethod
        def resolver(texto: str) -> str:
            for marcador, schema in trocas:
                texto = texto.replace(marcador, schema)
            return texto

        def execute(self, query, vars=None):
            if isinstance(query, str):
                query = self.resolver(query)
            return super().execute(query, vars)

    return CursorComSchemas


def conectar(cfg: Config):
    opcoes = f"-c search_path={cfg.schema_stg}"
    fabrica = criar_classe_cursor(cfg)
    if cfg.database_url:
        return psycopg2.connect(cfg.database_url, options=opcoes, cursor_factory=fabrica, **KEEPALIVES)
    faltando = [nome for nome, valor in (("PGHOST", cfg.pg_host), ("PGDATABASE", cfg.pg_database),
                                         ("PGUSER", cfg.pg_user), ("PGPASSWORD", cfg.pg_password)) if not valor]
    if faltando:
        raise ErroConfiguracao("Preencha no .env: " + ", ".join(faltando))
    return psycopg2.connect(
        host=cfg.pg_host, port=cfg.pg_port, dbname=cfg.pg_database, user=cfg.pg_user, password=cfg.pg_password,
        sslmode=cfg.pg_sslmode, options=opcoes, cursor_factory=fabrica, **KEEPALIVES,
    )


def _versao_aplicada(cur) -> Optional[str]:
    cur.execute("SELECT to_regclass('@STG@.ctl_schema')")
    if cur.fetchone()[0] is None:
        return None
    cur.execute("SELECT versao FROM @STG@.ctl_schema WHERE id = 1")
    linha = cur.fetchone()
    return linha[0] if linha else None


def aplicar_schema(cur, forcar: bool = False) -> bool:
    """Aplica o DDL so quando o arquivo ou os nomes dos schemas mudaram (hash do texto ja resolvido em ctl_schema)."""
    texto = cur.resolver(SCHEMA_SQL.read_text(encoding="utf-8"))
    versao = hashlib.sha256(texto.encode("utf-8")).hexdigest()
    if not forcar and _versao_aplicada(cur) == versao:
        return False
    cur.execute(texto)
    cur.execute(
        "INSERT INTO @STG@.ctl_schema (id, versao) VALUES (1, %s) "
        "ON CONFLICT (id) DO UPDATE SET versao = EXCLUDED.versao, aplicado_em = now()", (versao,))
    return True


def buscar_hashes(cur, ids: Sequence[int]) -> Dict[int, str]:
    if not ids:
        return {}
    cur.execute("SELECT id, hash_registro FROM @STG@.stg_viagem WHERE id = ANY(%s)", (list(ids),))
    return dict(cur.fetchall())


def gravar_staging(cur, registros: Sequence[dict], hashes: Dict[int, str], ida, ret) -> None:
    """Grava o JSON exatamente como a API devolveu (o SQL ja vai com os schemas resolvidos; os dados nao sao tocados)."""
    linhas = [(x["id"], ida, ret, Json(x), hashes[x["id"]]) for x in registros]
    execute_values(cur, cur.resolver(UPSERT_STAGING), linhas, page_size=200)


def contar_na_staging(cur, ids: Sequence[int]) -> int:
    if not ids:
        return 0
    cur.execute("SELECT count(*) FROM @STG@.stg_viagem WHERE id = ANY(%s)", (list(ids),))
    return cur.fetchone()[0]
