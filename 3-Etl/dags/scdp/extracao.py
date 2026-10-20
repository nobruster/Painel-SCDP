"""Extracao: unico ponto de contato com a API do Portal da Transparencia."""
from __future__ import annotations

import datetime as dt
import logging
import time
from typing import Callable, List, Optional, Tuple

import requests

from .config import Config
from .janelas import faixa

log = logging.getLogger("scdp.extracao")

BRASILIA = dt.timezone(dt.timedelta(hours=-3))
HORA_FIM_DA_MADRUGADA = 6
PERMANENTES = (400, 401, 403, 404)
ESPERA_PADRAO_429_S = 60
ESPERA_MAXIMA_429_S = 300


class ErroPermanente(Exception):
    """Erro que nao adianta repetir (400 parametro invalido, 401/403 chave invalida ou bloqueada, 404)."""

    def __init__(self, codigo: int, mensagem: str):
        super().__init__(f"{codigo} {mensagem}")
        self.codigo = codigo


def espera_retry_after(valor: Optional[str]) -> int:
    """Retry-After pode vir em segundos ou como data HTTP; qualquer coisa diferente de inteiro usa o padrao."""
    try:
        return max(1, min(int(valor), ESPERA_MAXIMA_429_S))
    except (TypeError, ValueError):
        return ESPERA_PADRAO_429_S


class ClienteApi:
    def __init__(
        self,
        cfg: Config,
        sessao: Optional[requests.Session] = None,
        dormir: Callable[[float], None] = time.sleep,
        agora: Optional[Callable[[], dt.datetime]] = None,
    ):
        self.cfg = cfg
        self.sessao = sessao or requests.Session()
        self.sessao.headers.update({"chave-api-dados": cfg.chave_api, "Accept": "application/json"})
        self.dormir = dormir
        self.agora = agora or (lambda: dt.datetime.now(BRASILIA))

    def pausar(self) -> None:
        """Respeita o limite do portal (400/min de dia, 700/min na madrugada, no horario de Brasilia)."""
        limite = self.cfg.limite_noite if self.agora().hour < HORA_FIM_DA_MADRUGADA else self.cfg.limite_dia
        self.dormir(60 / (limite * self.cfg.uso_do_limite))

    def _get(self, params: dict) -> list:
        url = f"{self.cfg.url_base}/viagens"
        for tentativa in range(1, self.cfg.tentativas_http + 1):
            dados = None
            try:
                r = self.sessao.get(url, params=params, timeout=self.cfg.timeout_http)
                if r.status_code == 200:
                    dados = r.json()
            except (requests.RequestException, ValueError) as e:
                log.warning("%s, tentativa %d", type(e).__name__, tentativa)
                self.dormir(4 * tentativa)
                continue
            if r.status_code == 200:
                self.pausar()
                return dados
            if r.status_code in PERMANENTES:
                raise ErroPermanente(r.status_code, self.cfg.sanitizar(r.text[:150]))
            log.warning("status %d, tentativa %d", r.status_code, tentativa)
            if r.status_code == 429:
                self.dormir(espera_retry_after(r.headers.get("Retry-After")))
                continue
            self.dormir(4 * tentativa)
        raise RuntimeError(f"API indisponivel apos {self.cfg.tentativas_http} tentativas")

    def buscar(self, ida, ret) -> Tuple[List[dict], int]:
        """Todas as viagens da janela (ida no mes `ida`, retorno no mes `ret`), paginando ate `[]`."""
        ia, ib = faixa(ida)
        ra, rb = faixa(ret)
        base = dict(dataIdaDe=ia, dataIdaAte=ib, dataRetornoDe=ra, dataRetornoAte=rb, codigoOrgao=self.cfg.orgao)
        registros: List[dict] = []
        pagina = 1
        while True:
            dados = self._get({**base, "pagina": pagina})
            if not dados:
                return registros, pagina - 1
            registros += dados
            pagina += 1
