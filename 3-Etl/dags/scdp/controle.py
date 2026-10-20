"""Controle e observabilidade (schema staging): janelas, erros abertos e resolvidos, execucoes."""
from __future__ import annotations

import datetime as dt
from typing import Callable, Dict, Optional, Tuple

Janela = Tuple[dt.date, dt.date]


class Controle:
    def __init__(self, cur, conn, orgao: str, sanitizar: Optional[Callable[[object], str]] = None):
        self.cur = cur
        self.conn = conn
        self.orgao = orgao
        self.sanitizar = sanitizar or str
        self.execucao_id: Optional[int] = None

    # ---- janelas
    def ler_estados(self) -> Dict[Janela, dict]:
        self.cur.execute("SELECT ida_mes, retorno_mes, status, qtd_api, fim FROM @STG@.ctl_janela WHERE orgao=%s", (self.orgao,))
        return {(r[0], r[1]): dict(status=r[2], qtd_api=r[3], fim=r[4]) for r in self.cur.fetchall()}

    def iniciar_janela(self, ida, ret) -> None:
        self.cur.execute(
            """INSERT INTO @STG@.ctl_janela (orgao, ida_mes, retorno_mes, status, tentativas, inicio)
               VALUES (%s,%s,%s,'EXECUTANDO',1,now())
               ON CONFLICT (orgao, ida_mes, retorno_mes)
               DO UPDATE SET status='EXECUTANDO', tentativas=@STG@.ctl_janela.tentativas+1, inicio=now(), erro=NULL""",
            (self.orgao, ida, ret))
        self.conn.commit()

    def concluir_janela(self, ida, ret, ok: bool, paginas: int, qtd_api: int, carregadas: int,
                        novos: int, alterados: int, aviso: Optional[str]) -> None:
        self.cur.execute(
            """UPDATE @STG@.ctl_janela SET status=%s, paginas_lidas=%s, qtd_api=%s, qtd_carregada=%s, qtd_novos=%s,
               qtd_alterados=%s, aviso=%s, erro=%s, fim=now() WHERE orgao=%s AND ida_mes=%s AND retorno_mes=%s""",
            ("OK" if ok else "ERRO", paginas, qtd_api, carregadas, novos, alterados, aviso,
             None if ok else f"carregadas {carregadas} de {qtd_api}", self.orgao, ida, ret))

    def falhar_janela(self, ida, ret, mensagem: str) -> None:
        self.cur.execute(
            "UPDATE @STG@.ctl_janela SET status='ERRO', erro=%s, fim=now() WHERE orgao=%s AND ida_mes=%s AND retorno_mes=%s",
            (self.sanitizar(mensagem)[:500], self.orgao, ida, ret))
        self.conn.commit()

    def contar_pendentes(self) -> int:
        self.cur.execute("SELECT count(*) FROM @STG@.ctl_janela WHERE orgao=%s AND status<>'OK'", (self.orgao,))
        return self.cur.fetchone()[0]

    # ---- erros
    def _chave(self, ida, ret, etapa: str) -> str:
        return f"{self.orgao}|{ida}|{ret}|{etapa}"

    def registrar_erro(self, ida, ret, etapa: str, mensagem: str, codigo: Optional[str] = None) -> None:
        self.cur.execute(
            """INSERT INTO @STG@.ctl_erro (chave, orgao, ida_mes, retorno_mes, etapa, codigo, mensagem, execucao_id)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
               ON CONFLICT (chave) DO UPDATE SET mensagem = EXCLUDED.mensagem, codigo = EXCLUDED.codigo,
                   tentativas = @STG@.ctl_erro.tentativas + 1, ultima_ocorrencia = now(), execucao_id = EXCLUDED.execucao_id""",
            (self._chave(ida, ret, etapa), self.orgao, ida, ret, etapa, codigo, self.sanitizar(mensagem or "")[:500], self.execucao_id))
        self.conn.commit()

    def resolver_erros(self, ida, ret, etapa: Optional[str] = None) -> None:
        """Tira o erro de ctl_erro e guarda em ctl_erro_historico. Quem chama faz o commit."""
        self.cur.execute(
            """WITH r AS (
                   DELETE FROM @STG@.ctl_erro
                   WHERE orgao = %s AND ida_mes IS NOT DISTINCT FROM %s AND retorno_mes IS NOT DISTINCT FROM %s
                     AND (%s::text IS NULL OR etapa = %s)
                   RETURNING chave, orgao, ida_mes, retorno_mes, etapa, codigo, mensagem, tentativas,
                             primeira_ocorrencia, ultima_ocorrencia, execucao_id)
               INSERT INTO @STG@.ctl_erro_historico (chave, orgao, ida_mes, retorno_mes, etapa, codigo, mensagem,
                   tentativas, primeira_ocorrencia, ultima_ocorrencia, execucao_id, resolvido_na_execucao)
               SELECT chave, orgao, ida_mes, retorno_mes, etapa, codigo, mensagem, tentativas,
                   primeira_ocorrencia, ultima_ocorrencia, execucao_id, %s FROM r""",
            (self.orgao, ida, ret, etapa, etapa, self.execucao_id))

    def contar_abertos(self) -> int:
        self.cur.execute("SELECT count(*) FROM @STG@.ctl_erro WHERE orgao=%s", (self.orgao,))
        return self.cur.fetchone()[0]

    # ---- execucoes
    def marcar_execucoes_interrompidas(self, horas: int = 12) -> None:
        """Execucao sem fim ha mais de `horas` caiu no meio: marca e gera erro da etapa 'execucao'."""
        self.cur.execute(
            """UPDATE @STG@.ctl_execucao SET status = 'INTERROMPIDA', fim = now()
               WHERE fim IS NULL AND (status IS NULL OR status = 'EXECUTANDO')
                 AND inicio < now() - make_interval(hours => %s)
               RETURNING id""", (horas,))
        for (rid,) in self.cur.fetchall():
            self.cur.execute(
                """INSERT INTO @STG@.ctl_erro (chave, orgao, etapa, mensagem, execucao_id) VALUES (%s,%s,'execucao',%s,%s)
                   ON CONFLICT (chave) DO NOTHING""",
                (f"execucao|{rid}", self.orgao, "execucao interrompida sem registrar o fim; janelas pendentes serao retomadas", rid))
        self.conn.commit()

    def iniciar_execucao(self, modo: str, janelas_total: int) -> int:
        self.cur.execute(
            "INSERT INTO @STG@.ctl_execucao (modo, janelas_total, status) VALUES (%s,%s,'EXECUTANDO') RETURNING id",
            (modo, janelas_total))
        self.execucao_id = self.cur.fetchone()[0]
        self.conn.commit()
        return self.execucao_id

    def interromper_execucao(self, status: str = "INTERROMPIDA") -> None:
        """Fecha a execucao atual sem concluir (SIGTERM do Airflow no timeout, erro de banco)."""
        if self.execucao_id is None:
            return
        self.cur.execute("UPDATE @STG@.ctl_execucao SET fim=now(), status=%s WHERE id=%s", (status, self.execucao_id))
        self.conn.commit()

    def finalizar_execucao(self, status: str, lidas: int, erros: int, novos: int, alterados: int) -> None:
        self.cur.execute(
            """UPDATE @STG@.ctl_execucao SET fim=now(), status=%s, janelas_lidas=%s, janelas_erro=%s, novos=%s, alterados=%s
               WHERE id=%s""", (status, lidas, erros, novos, alterados, self.execucao_id))
        self.conn.commit()
