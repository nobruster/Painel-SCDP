from __future__ import annotations

import argparse
import datetime as dt
import logging
import sys
from typing import List, Optional

from . import carga
from .config import Config, ErroConfiguracao
from .controle import Controle
from .extracao import ClienteApi
from .janelas import planejar
from .pipeline import Pipeline

log = logging.getLogger("scdp")


def mes_ano(valor: str) -> dt.date:
    try:
        return dt.datetime.strptime(valor, "%Y-%m").date()
    except ValueError:
        raise argparse.ArgumentTypeError(f"use o formato AAAA-MM (recebido: {valor!r})")


def criar_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description="Carga incremental das viagens do SCDP")
    ap.add_argument("--desde", type=mes_ano, default=dt.date(2025, 1, 1), help="mes inicial de ida (AAAA-MM)")
    ap.add_argument("--modo", choices=["diario", "completo"], default="diario",
                    help="diario: janelas dos ultimos 3 meses + pendentes; completo: todas as janelas desde --desde")
    ap.add_argument("--reconstruir-silver", action="store_true",
                    help="recria a intermediaria e a analitica a partir de toda a staging, sem chamar a API")
    ap.add_argument("--dry-run", action="store_true", help="so consulta a API e conta, sem banco")
    return ap


def main(argv: Optional[List[str]] = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s", datefmt="%H:%M:%S")
    args = criar_parser().parse_args(argv)
    try:
        cfg = Config.do_ambiente()
    except ErroConfiguracao as e:
        log.error("%s", e)
        return 2
    desde = args.desde
    hoje = dt.date.today()
    extrator = ClienteApi(cfg)

    if args.dry_run:
        total = 0
        for ida, ret in planejar(desde, hoje, cfg):
            registros, _ = extrator.buscar(ida, ret)
            total += len(registros)
            if registros:
                log.info("ida %s -> ret %s: %d", f"{ida:%Y-%m}", f"{ret:%Y-%m}", len(registros))
        log.info("TOTAL %d", total)
        return 0

    try:
        conn = carga.conectar(cfg)
    except ErroConfiguracao as e:
        log.error("%s", e)
        return 2
    try:
        cur = conn.cursor()
        carga.aplicar_schema(cur)
        conn.commit()
        pipeline = Pipeline(cfg, conn, extrator, Controle(cur, conn, cfg.orgao, sanitizar=cfg.sanitizar))
        if args.reconstruir_silver:
            return pipeline.reconstruir()
        return pipeline.executar(args.modo, desde, hoje)
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
