"""Pipeline: orquestra extracao -> carga (staging) -> transformacao, janela a janela, com controle de erros e retomada."""
from __future__ import annotations

import datetime as dt
import logging
import time
from dataclasses import dataclass
from typing import Callable, Dict, Optional, Tuple

import psycopg2

from . import carga, janelas, transformacao
from .config import Config
from .controle import Controle
from .extracao import ErroPermanente

log = logging.getLogger("scdp.pipeline")

CODIGOS_FATAIS = (401, 403)
CODIGO_OCUPADO = 3
RELEITURAS_POR_QUEDA = 2
PAUSA_RELEITURA_S = 10
PAUSA_RODADA_S = 30


class ErroFatal(Exception):
    """Falha que torna inutil continuar a execucao (chave invalida ou bloqueada, conexao com o banco perdida)."""


@dataclass
class ResultadoJanela:
    ok: bool
    qtd: int = 0
    novos: int = 0
    alterados: int = 0
    aviso: Optional[str] = None


class Pipeline:
    def __init__(self, cfg: Config, conn, extrator, controle: Controle, dormir: Callable[[float], None] = time.sleep):
        self.cfg = cfg
        self.conn = conn
        self.cur = conn.cursor()
        self.extrator = extrator
        self.controle = controle
        self.dormir = dormir

    # ---- trava: uma execucao por vez por orgao (evita perder viagens na marca d'agua da analitica)
    def _chave_trava(self) -> str:
        return f"scdp:{self.cfg.orgao}"

    def _obter_trava(self) -> bool:
        self.cur.execute("SELECT pg_try_advisory_lock(hashtext(%s))", (self._chave_trava(),))
        obtida = self.cur.fetchone()[0]
        self.conn.commit()
        return obtida

    def _liberar_trava(self) -> None:
        try:
            self.conn.rollback()
            self.cur.execute("SELECT pg_advisory_unlock(hashtext(%s))", (self._chave_trava(),))
            self.conn.commit()
        except psycopg2.Error:
            pass

    # ---- uma janela
    def _falha(self, ida, ret, etapa: str, erro: Exception, codigo: Optional[str]) -> None:
        mensagem = self.cfg.sanitizar(erro)
        try:
            self.conn.rollback()
            self.controle.falhar_janela(ida, ret, mensagem)
            self.controle.registrar_erro(ida, ret, etapa, mensagem, codigo=codigo)
        except psycopg2.Error as e:
            raise ErroFatal(f"conexao com o banco perdida ao registrar o erro ({type(e).__name__})") from e

    def processar_janela(self, ida: dt.date, ret: dt.date, estado: Optional[dict]) -> ResultadoJanela:
        c = self.controle
        c.iniciar_janela(ida, ret)
        etapa = "api"
        try:
            registros, paginas = self.extrator.buscar(ida, ret)
            anterior = estado["qtd_api"] if estado else None
            for _ in range(RELEITURAS_POR_QUEDA):
                if not (anterior and len(registros) < anterior):
                    break
                self.dormir(PAUSA_RELEITURA_S)
                registros, paginas = self.extrator.buscar(ida, ret)
            avisos = []
            if anterior and len(registros) < anterior:
                avisos.append(f"queda de {anterior} para {len(registros)} registros")

            etapa = "banco"
            registros, repetidos = transformacao.remover_repetidos(registros)
            if repetidos:
                avisos.append(f"{repetidos} registros repetidos pela API foram ignorados")
            aviso = "; ".join(avisos) or None

            ids = [x["id"] for x in registros]
            novos, alterados, hashes = transformacao.classificar(registros, carga.buscar_hashes(self.cur, ids))
            mudaram = novos + alterados
            if mudaram:
                carga.gravar_staging(self.cur, mudaram, hashes, ida, ret)
                transformacao.atualizar_intermediaria(self.cur, [x["id"] for x in mudaram])

            carregadas = carga.contar_na_staging(self.cur, ids)
            ok = carregadas == len(ids)
            c.concluir_janela(ida, ret, ok, paginas, len(ids), carregadas, len(novos), len(alterados), aviso)
            if ok:
                c.resolver_erros(ida, ret)
            self.conn.commit()
            if not ok:
                c.registrar_erro(ida, ret, "conciliacao", f"carregadas {carregadas} de {len(ids)}")
            return ResultadoJanela(ok, len(registros), len(novos), len(alterados), aviso)
        except ErroPermanente as e:
            self._falha(ida, ret, etapa, e, codigo=str(e.codigo))
            if e.codigo in CODIGOS_FATAIS:
                raise ErroFatal(self.cfg.sanitizar(e)) from e
            return ResultadoJanela(False, aviso=self.cfg.sanitizar(e)[:120])
        except Exception as e:
            log.warning("janela %s -> %s falhou na etapa %s: %s: %s", f"{ida:%Y-%m}", f"{ret:%Y-%m}", etapa,
                        type(e).__name__, self.cfg.sanitizar(e)[:200])
            self._falha(ida, ret, etapa, e, codigo=type(e).__name__)
            return ResultadoJanela(False, aviso=self.cfg.sanitizar(e)[:120])

    # ---- analitica
    def atualizar_analitica_registrando(self) -> Tuple[int, bool]:
        """Falha na analitica vira erro registrado; a marca d'agua so avanca no sucesso, entao a proxima execucao refaz."""
        try:
            qtd = transformacao.atualizar_analitica(self.cur)
            self.controle.resolver_erros(None, None, etapa="analitica")
            self.conn.commit()
            return qtd, True
        except Exception as e:
            self.conn.rollback()
            self.controle.registrar_erro(None, None, "analitica", self.cfg.sanitizar(e), codigo=type(e).__name__)
            return 0, False

    def reconstruir(self) -> int:
        if not self._obter_trava():
            log.warning("outra execucao da carga esta em andamento; nada foi reconstruido")
            return CODIGO_OCUPADO
        try:
            transformacao.atualizar_intermediaria(self.cur)
            self.cur.execute("SELECT count(*) FROM @INT@.int_viagem")
            log.info("intermediaria reconstruida: %d registros", self.cur.fetchone()[0])
            log.info("analitica reconstruida: %d viagens", transformacao.atualizar_analitica(self.cur, tudo=True))
            self.conn.commit()
            return 0
        finally:
            self._liberar_trava()

    # ---- execucao
    def executar(self, modo: str, desde: dt.date, hoje: dt.date) -> int:
        """Roda a carga. 0 = limpa; 1 = sobrou erro, pendencia ou foi abortada; 3 = outra execucao em andamento."""
        if not self._obter_trava():
            log.warning("outra execucao da carga esta em andamento para o orgao %s; encerrando", self.cfg.orgao)
            return CODIGO_OCUPADO
        try:
            return self._executar(modo, desde, hoje)
        except psycopg2.Error as e:
            log.error("execucao encerrada por erro de banco: %s", type(e).__name__)
            return 1
        finally:
            self._liberar_trava()

    def _executar(self, modo: str, desde: dt.date, hoje: dt.date) -> int:
        cfg, c = self.cfg, self.controle
        todas = list(janelas.planejar(desde, hoje, cfg))
        c.marcar_execucoes_interrompidas(cfg.horas_execucao_interrompida)
        c.iniciar_execucao(modo, len(todas))
        estados = c.ler_estados()

        limite_recente = janelas.add_meses(hoje.replace(day=1), -cfg.meses_recentes)
        lidas = novos = alterados = tardios = 0
        abortou = False
        falhas: Dict[janelas.Janela, Optional[dict]] = {}

        for ida, ret in janelas.ordenar_janelas(todas, estados):
            est = estados.get((ida, ret))
            if not janelas.precisa_ler(est, ida, ret, hoje, modo, cfg):
                continue
            try:
                r = self.processar_janela(ida, ret, est)
            except ErroFatal as e:
                log.error("ABORTADO: %s", cfg.sanitizar(e))
                abortou = True
                break
            lidas += 1
            novos += r.novos
            alterados += r.alterados
            if not r.ok:
                falhas[(ida, ret)] = est
            atrasado = r.novos > 0 and est is not None and est["status"] == "OK" and ida < limite_recente
            tardios += r.novos if atrasado else 0
            if r.qtd or r.novos or r.alterados or r.aviso or not r.ok:
                log.info("ida %s -> ret %s: api=%d novos=%d alterados=%d%s%s%s", f"{ida:%Y-%m}", f"{ret:%Y-%m}", r.qtd,
                         r.novos, r.alterados, " TARDIO" if atrasado else "", f" AVISO {r.aviso}" if r.aviso else "",
                         "" if r.ok else " ERRO")

        for rodada in range(1, cfg.rodadas_retentativa + 1):
            if not falhas or abortou:
                break
            log.info("nova tentativa das janelas com erro (rodada %d): %d", rodada, len(falhas))
            self.dormir(PAUSA_RODADA_S * rodada)
            for (ida, ret), est in list(falhas.items()):
                try:
                    r = self.processar_janela(ida, ret, est)
                except ErroFatal as e:
                    log.error("ABORTADO: %s", cfg.sanitizar(e))
                    abortou = True
                    break
                novos += r.novos
                alterados += r.alterados
                if r.ok:
                    del falhas[(ida, ret)]
                    log.info("ida %s -> ret %s: corrigido (api=%d novos=%d)", f"{ida:%Y-%m}", f"{ret:%Y-%m}", r.qtd, r.novos)

        erros = len(falhas)
        analiticas, ok_analitica = self.atualizar_analitica_registrando()
        log.info("analitica: %d viagens processadas%s", analiticas, "" if ok_analitica else " (ERRO, registrado)")
        pendentes = c.contar_pendentes()
        limpo = not erros and not pendentes and ok_analitica and not abortou
        if limpo:
            c.resolver_erros(None, None, etapa="execucao")
        status = "CONCLUIDA" if limpo else ("ABORTADA" if abortou else "COM_ERROS")
        c.finalizar_execucao(status, lidas, erros, novos, alterados)
        abertos = c.contar_abertos()
        log.info("janelas planejadas=%d lidas=%d erro=%d pendentes=%d erros_abertos=%d novos=%d alterados=%d tardios=%d status=%s",
                 len(todas), lidas, erros, pendentes, abertos, novos, alterados, tardios, status)
        return 1 if (abertos or pendentes or abortou) else 0
