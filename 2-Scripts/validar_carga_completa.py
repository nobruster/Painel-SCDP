"""Uso: python -I 2-Scripts/validar_carga_completa.py [--desde YYYY-MM]  ->  CARGA=OK|DIVERGENTE|NAO_MEDIDO|ERRO (exit 0 so em OK).

Gate: toda janela planejada desde `--desde` (padrao 2025-01) existe em ctl_janela, esta OK e tem qtd_api = qtd_carregada.
"""
import argparse
import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "3-Etl" / "dags"))

from scdp import carga, janelas  # noqa: E402
from scdp.config import Config  # noqa: E402
from scdp.reconciliacao import DIVERGENTE, NAO_MEDIDO, OK, Resultado  # noqa: E402

MAX_LISTADAS = 20


def verificar(cur, orgao: str, planejadas) -> Resultado:
    planejadas = list(planejadas)
    cur.execute(
        "SELECT ida_mes, retorno_mes, status, qtd_api, qtd_carregada FROM @STG@.ctl_janela WHERE orgao = %s", (orgao,))
    existentes = {(r[0], r[1]): r[2:] for r in cur.fetchall()}
    medidas = {"planejadas": len(planejadas), "registradas": len(existentes)}
    if not existentes:
        return Resultado(NAO_MEDIDO, medidas, ["ctl_janela vazia: nenhuma janela foi lida"])

    faltando, fora_de_ok, divergentes = [], [], []
    for ida, ret in planejadas:
        nome = f"{ida:%Y-%m}/{ret:%Y-%m}"
        if (ida, ret) not in existentes:
            faltando.append(nome)
            continue
        status, qtd_api, qtd_carregada = existentes[(ida, ret)]
        if status != "OK":
            fora_de_ok.append(f"{nome} ({status})")
        elif qtd_api is None or qtd_api != qtd_carregada:
            divergentes.append(f"{nome} (api {qtd_api}, carregada {qtd_carregada})")
    medidas.update(sem_registro=len(faltando), fora_de_ok=len(fora_de_ok), qtd_diferente=len(divergentes))

    motivos = []
    for rotulo, itens in (("janelas planejadas sem registro", faltando), ("janelas fora de OK", fora_de_ok),
                          ("janelas com qtd_api != qtd_carregada", divergentes)):
        if itens:
            resto = f" e mais {len(itens) - MAX_LISTADAS}" if len(itens) > MAX_LISTADAS else ""
            motivos.append(f"{len(itens)} {rotulo}: {', '.join(itens[:MAX_LISTADAS])}{resto}")
    return Resultado(DIVERGENTE if motivos else OK, medidas, motivos)


def _mes(texto: str) -> dt.date:
    return dt.datetime.strptime(texto, "%Y-%m").date()


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--desde", type=_mes, default=dt.date(2025, 1, 1), help="primeiro mes de ida (YYYY-MM)")
    args = p.parse_args(argv)
    try:
        cfg = Config.do_ambiente()
        with carga.conectar(cfg) as conn, conn.cursor() as cur:
            r = verificar(cur, cfg.orgao, janelas.planejar(args.desde, dt.date.today(), cfg))
    except Exception as e:
        print(f"CARGA=ERRO ({type(e).__name__})")
        return 1
    for k, v in r.medidas.items():
        print(f"{k:28} {v}")
    for motivo in r.motivos:
        print("-", motivo)
    print(f"CARGA={r.veredito}")
    return 0 if r.veredito == OK else 1


if __name__ == "__main__":
    sys.exit(main())
