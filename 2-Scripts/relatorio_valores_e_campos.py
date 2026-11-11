"""Somas de diarias, passagens e total por mes (int_viagem) e inventario dos campos da API (stg_viagem).

Uso: python -I 2-Scripts/relatorio_valores_e_campos.py --ano 2026 [--orgao 33000] [--so-valores | --so-campos]
Campo "preenchido" = diferente de nulo, texto vazio e zero. Somente leitura; exit 0 em sucesso, 1 em erro.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from decimal import Decimal
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "3-Etl" / "dags"))

from scdp import carga  # noqa: E402
from scdp.config import Config  # noqa: E402

SQL_VALORES = (
    "SELECT extract(month FROM data_inicio)::int, count(*), coalesce(sum(valor_diarias), 0), "
    "coalesce(sum(valor_passagem), 0), coalesce(sum(valor_total_viagem), 0) FROM @INT@.int_viagem "
    "WHERE orgao_siafi = %s AND extract(year FROM data_inicio) = %s GROUP BY 1 ORDER BY 1"
)
SQL_PAYLOADS = (
    "SELECT s.payload FROM @STG@.stg_viagem s JOIN @INT@.int_viagem i USING (id) "
    "WHERE i.orgao_siafi = %s AND extract(year FROM i.data_inicio) = %s"
)


def brl(valor) -> str:
    return f"{Decimal(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def somas_por_mes(cur, orgao: str, ano: int) -> List[tuple]:
    cur.execute(SQL_VALORES, (orgao, ano))
    return [tuple(r) for r in cur.fetchall()]


def imprimir_valores(linhas: List[tuple], log=print) -> None:
    log(f"{'mes':>3} {'viagens':>8} {'diarias':>16} {'passagens':>16} {'total':>16}")
    tot = [0, Decimal(0), Decimal(0), Decimal(0)]
    for mes, qtd, dia, pas, total in linhas:
        log(f"{mes:>3} {qtd:>8} {brl(dia):>16} {brl(pas):>16} {brl(total):>16}")
        tot = [tot[0] + qtd, tot[1] + Decimal(dia), tot[2] + Decimal(pas), tot[3] + Decimal(total)]
    log(f"{'ano':>3} {tot[0]:>8} {brl(tot[1]):>16} {brl(tot[2]):>16} {brl(tot[3]):>16}")
    log(f"diarias + passagens: {brl(tot[1] + tot[2])}")


def preenchido(v) -> bool:
    if v is None or isinstance(v, bool):
        return v is True
    if isinstance(v, (str, list, dict)):
        return len(v.strip() if isinstance(v, str) else v) > 0
    return v != 0


def caminhos(obj, prefixo: str = "") -> Iterable[Tuple[str, object]]:
    """Cada folha do JSON como (caminho, valor); listas viram `[]` no caminho; objeto/lista vazios contam como folha."""
    if isinstance(obj, dict) and obj:
        for k, v in obj.items():
            yield from caminhos(v, f"{prefixo}.{k}" if prefixo else k)
    elif isinstance(obj, list) and obj:
        for v in obj:
            yield from caminhos(v, prefixo + "[]")
    else:
        yield prefixo, obj


def inventario(payloads: Iterable[object]) -> Tuple[int, Dict[str, List[int]]]:
    """(total de viagens, {caminho: [viagens com o campo, viagens com o campo preenchido]})."""
    total, presente, cheio = 0, Counter(), Counter()
    for p in payloads:
        if isinstance(p, (str, bytes)):
            p = json.loads(p)
        total += 1
        vistos, vistos_cheios = set(), set()
        for caminho, valor in caminhos(p):
            vistos.add(caminho)
            if preenchido(valor):
                vistos_cheios.add(caminho)
        presente.update(vistos)
        cheio.update(vistos_cheios)
    return total, {c: [presente[c], cheio[c]] for c in sorted(presente)}


def ler_payloads(cur, orgao: str, ano: int):
    cur.execute(SQL_PAYLOADS, (orgao, ano))
    while True:
        lote = cur.fetchmany(1000)
        if not lote:
            return
        for (payload,) in lote:
            yield payload


def imprimir_inventario(total: int, campos: Dict[str, List[int]], log=print) -> None:
    log(f"campos da API em {total} viagens (presente / preenchido):")
    for caminho, (pres, cheio) in campos.items():
        log(f"  {caminho:<52} {pres:>6} {cheio:>6}" + ("  sempre vazio" if total and cheio == 0 else ""))


def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--ano", type=int, required=True)
    p.add_argument("--orgao", help="padrao: CODIGO_ORGAO do .env")
    grupo = p.add_mutually_exclusive_group()
    grupo.add_argument("--so-valores", action="store_true")
    grupo.add_argument("--so-campos", action="store_true")
    a = p.parse_args(argv)
    try:
        cfg = Config.do_ambiente()
        orgao = a.orgao or cfg.orgao
        with carga.conectar(cfg) as conn, conn.cursor() as cur:
            print(f"orgao {orgao}, ano {a.ano}")
            if not a.so_campos:
                imprimir_valores(somas_por_mes(cur, orgao, a.ano))
            if not a.so_valores:
                imprimir_inventario(*inventario(ler_payloads(cur, orgao, a.ano)))
    except Exception as e:
        print(f"ERRO ({type(e).__name__}) {str(e)[:150]}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
