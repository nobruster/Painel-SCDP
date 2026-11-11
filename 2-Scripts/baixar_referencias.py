"""Baixa a spec Swagger (/v3/api-docs) e as listas de orgaos SIAFI e SIAPE.

Uso: python -I 2-Scripts/baixar_referencias.py [--dry-run] [--destino 1-Documentos/referencia] [--spec 2-Scripts/saidas/api-docs.json]
Grava orgaos_siafi.csv e orgaos_siape.csv (codigo;descricao, UTF-8 com BOM, CRLF). Com --dry-run nada e gravado.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Callable, List, Optional
from urllib.parse import urlsplit

import requests

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "3-Etl" / "dags"))

from scdp.config import Config  # noqa: E402
from scdp.extracao import ErroPermanente, MAX_PAGINAS, PERMANENTES, ClienteApi, espera_retry_after  # noqa: E402

LISTAS = {"orgaos_siafi.csv": "orgaos-siafi", "orgaos_siape.csv": "orgaos-siape"}


def url_spec(cfg: Config) -> str:
    partes = urlsplit(cfg.url_base)
    return f"{partes.scheme}://{partes.netloc}/v3/api-docs"


def obter(cliente: ClienteApi, url: str, params: Optional[dict] = None):
    cfg = cliente.cfg
    for tentativa in range(1, cfg.tentativas_http + 1):
        try:
            r = cliente.sessao.get(url, params=params, timeout=cfg.timeout_http, allow_redirects=False)
            if r.status_code == 200:
                dados = r.json()
                cliente.pausar()
                return dados
        except (requests.RequestException, ValueError):
            cliente.dormir(4 * tentativa)
            continue
        if r.status_code in PERMANENTES or 300 <= r.status_code < 400:
            raise ErroPermanente(r.status_code, cfg.sanitizar(r.text)[:150])
        cliente.dormir(espera_retry_after(r.headers.get("Retry-After")) if r.status_code == 429 else 4 * tentativa)
    raise RuntimeError(f"API indisponivel apos {cfg.tentativas_http} tentativas")


def listar_orgaos(cliente: ClienteApi, endpoint: str) -> List[dict]:
    linhas, anterior = [], None
    for pagina in range(1, MAX_PAGINAS + 1):
        dados = obter(cliente, f"{cliente.cfg.url_base}/{endpoint}", {"pagina": pagina})
        if not dados:
            break
        codigos = [x.get("codigo") for x in dados]
        if codigos == anterior:
            raise RuntimeError(f"{endpoint}: a API devolveu a pagina {pagina - 1} de novo")
        anterior = codigos
        linhas += dados
    unicos = {str(x["codigo"]).strip(): str(x.get("descricao") or "").strip() for x in linhas}
    return [{"codigo": k, "descricao": unicos[k]} for k in sorted(unicos)]


def para_csv(orgaos: List[dict]) -> bytes:
    texto = "\r\n".join(["codigo;descricao"] + [f"{o['codigo']};{o['descricao'].replace(';', ',')}" for o in orgaos])
    return ("﻿" + texto + "\r\n").encode("utf-8")


def _linhas_atuais(caminho: Path) -> str:
    if not caminho.exists():
        return "arquivo novo"
    return f"{max(len(caminho.read_bytes().splitlines()) - 1, 0)} orgaos hoje"


def baixar(cliente: ClienteApi, destino: Path, spec: Path, dry_run: bool, log: Callable[[str], None] = print) -> int:
    api_docs = obter(cliente, url_spec(cliente.cfg))
    rotulo = "dry-run, nada gravado" if dry_run else "gravado"
    log(f"spec: {len(api_docs.get('paths', {}))} caminhos ({rotulo})")
    if not dry_run:
        spec.parent.mkdir(parents=True, exist_ok=True)
        spec.write_text(json.dumps(api_docs, ensure_ascii=False, indent=1), encoding="utf-8")
    for nome, endpoint in LISTAS.items():
        orgaos = listar_orgaos(cliente, endpoint)
        if not orgaos:
            raise RuntimeError(f"{endpoint} devolveu lista vazia; arquivo mantido")
        alvo = destino / nome
        log(f"{nome}: {len(orgaos)} orgaos ({_linhas_atuais(alvo)}; {rotulo})")
        if not dry_run:
            destino.mkdir(parents=True, exist_ok=True)
            alvo.write_bytes(para_csv(orgaos))
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--dry-run", action="store_true", help="baixa e conta, sem gravar nada")
    p.add_argument("--destino", type=Path, default=RAIZ / "1-Documentos" / "referencia")
    p.add_argument("--spec", type=Path, default=RAIZ / "2-Scripts" / "saidas" / "api-docs.json")
    a = p.parse_args(argv)
    try:
        return baixar(ClienteApi(Config.do_ambiente()), a.destino, a.spec, a.dry_run)
    except ErroPermanente as e:
        print(f"ERRO {e}")
    except Exception as e:
        print(f"ERRO ({type(e).__name__}) {str(e)[:150]}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
