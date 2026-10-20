from __future__ import annotations

import calendar
import datetime as dt
from typing import Dict, Iterable, Iterator, Optional, Tuple

from .config import Config

Janela = Tuple[dt.date, dt.date]
Estado = Dict[str, object]


def add_meses(d: dt.date, n: int) -> dt.date:
    m = d.month - 1 + n
    return dt.date(d.year + m // 12, m % 12 + 1, 1)


def faixa(d: dt.date) -> Tuple[str, str]:
    """Primeiro e ultimo dia do mes de `d`, no formato dd/MM/aaaa exigido pela API."""
    ultimo = calendar.monthrange(d.year, d.month)[1]
    return d.strftime("01/%m/%Y"), f"{ultimo:02d}/{d.month:02d}/{d.year}"


def planejar(desde: dt.date, hoje: dt.date, cfg: Config) -> Iterator[Janela]:
    """Todas as combinacoes mes de ida x mes de retorno (ate +12 meses), incluindo meses futuros de ida."""
    ate_ida = add_meses(hoje.replace(day=1), cfg.meses_futuros)
    ida = desde
    while ida <= ate_ida:
        for k in range(cfg.meses_retorno_apos_ida + 1):
            yield ida, add_meses(ida, k)
        ida = add_meses(ida, 1)


def precisa_ler(estado: Optional[Estado], ida: dt.date, ret: dt.date, hoje: dt.date, modo: str, cfg: Config) -> bool:
    if modo == "completo" or estado is None or estado["status"] != "OK":
        return True
    limite = add_meses(hoje.replace(day=1), -cfg.meses_recentes)
    return ida >= limite or ret >= limite


def ordenar_janelas(janelas: Iterable[Janela], estados: Dict[Janela, Estado]) -> list:
    """Retoma de onde parou: janelas com erro, interrompidas ou pendentes primeiro; o resto em ordem cronologica."""
    def grupo(j: Janela) -> int:
        est = estados.get(j)
        return 0 if (est is not None and est["status"] != "OK") else 1
    return sorted(janelas, key=grupo)
