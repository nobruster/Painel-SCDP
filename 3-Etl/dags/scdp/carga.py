"""Carga: tudo que escreve ou le a camada staging e a conexao com o PostgreSQL."""
from __future__ import annotations

from pathlib import Path
from typing import Dict, Sequence

import psycopg2
from psycopg2.extras import Json, execute_values

from .config import Config, ErroConfiguracao

SCHEMA_SQL = Path(__file__).resolve().parent.parent / "sql" / "schema.sql"

UPSERT_STAGING = (
    "INSERT INTO @STG@.stg_viagem (id, janela_ida, janela_retorno, payload, hash_registro) VALUES %s "
    "ON CONFLICT (id) DO UPDATE SET janela_ida = EXCLUDED.janela_ida, janela_retorno = EXCLUDED.janela_retorno, "
    "payload = EXCLUDED.payload, hash_registro = EXCLUDED.hash_registro, atualizado_em = now()"
)


def criar_classe_cursor(cfg: Config):
    """Cursor que troca @STG@, @INT@ e @ANA@ pelos schemas configurados (tambem nas consultas em bytes do execute_values)."""
    trocas = (("@STG@", cfg.schema_stg), ("@INT@", cfg.schema_int), ("@ANA@", cfg.schema_ana))

    class CursorComSchemas(psycopg2.extensions.cursor):
        def execute(self, query, vars=None):
            eh_bytes = isinstance(query, bytes)
            texto = query.decode("utf-8") if eh_bytes else query
            if isinstance(texto, str):
                for marcador, schema in trocas:
                    texto = texto.replace(marcador, schema)
                query = texto.encode("utf-8") if eh_bytes else texto
            return super().execute(query, vars)

    return CursorComSchemas


def conectar(cfg: Config):
    opcoes = f"-c search_path={cfg.schema_stg}"
    fabrica = criar_classe_cursor(cfg)
    if cfg.database_url:
        return psycopg2.connect(cfg.database_url, options=opcoes, cursor_factory=fabrica)
    faltando = [nome for nome, valor in (("PGHOST", cfg.pg_host), ("PGDATABASE", cfg.pg_database),
                                         ("PGUSER", cfg.pg_user), ("PGPASSWORD", cfg.pg_password)) if not valor]
    if faltando:
        raise ErroConfiguracao("Preencha no .env: " + ", ".join(faltando))
    return psycopg2.connect(
        host=cfg.pg_host, port=cfg.pg_port, dbname=cfg.pg_database, user=cfg.pg_user, password=cfg.pg_password,
        sslmode=cfg.pg_sslmode, options=opcoes, cursor_factory=fabrica,
    )


def aplicar_schema(cur) -> None:
    cur.execute(SCHEMA_SQL.read_text(encoding="utf-8"))


def buscar_hashes(cur, ids: Sequence[int]) -> Dict[int, str]:
    if not ids:
        return {}
    cur.execute("SELECT id, hash_registro FROM @STG@.stg_viagem WHERE id = ANY(%s)", (list(ids),))
    return dict(cur.fetchall())


def gravar_staging(cur, registros: Sequence[dict], hashes: Dict[int, str], ida, ret) -> None:
    """Grava o JSON exatamente como a API devolveu."""
    linhas = [(x["id"], ida, ret, Json(x), hashes[x["id"]]) for x in registros]
    execute_values(cur, UPSERT_STAGING, linhas, page_size=200)


def contar_na_staging(cur, ids: Sequence[int]) -> int:
    if not ids:
        return 0
    cur.execute("SELECT count(*) FROM @STG@.stg_viagem WHERE id = ANY(%s)", (list(ids),))
    return cur.fetchone()[0]
