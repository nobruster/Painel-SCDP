"""Uso: python -I 2-Scripts/verificar_reconciliacao.py  ->  RECONCILIACAO=OK|DIVERGENTE|NAO_MEDIDO|ERRO (exit 0 so em OK)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "3-Etl" / "dags"))

from scdp import carga, reconciliacao  # noqa: E402
from scdp.config import Config  # noqa: E402


def main() -> int:
    try:
        cfg = Config.do_ambiente()
        with carga.conectar(cfg) as conn, conn.cursor() as cur:
            r = reconciliacao.reconciliar(cur)
    except Exception as e:
        print(f"RECONCILIACAO=ERRO ({type(e).__name__})")
        return 1
    for k, v in r.medidas.items():
        print(f"{k:28} {v}")
    for motivo in r.motivos:
        print("-", motivo)
    print(f"RECONCILIACAO={r.veredito}")
    return 0 if r.veredito == reconciliacao.OK else 1


if __name__ == "__main__":
    sys.exit(main())
