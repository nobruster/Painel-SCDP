"""Alerta de falha da carga: monta a mensagem sem segredos e envia por webhook HTTPS (ADR 0003).

A URL do webhook e segredo: vem de ALERTA_WEBHOOK_URL no ambiente do worker e nunca entra em mensagem nem em log.
Falha no envio nunca levanta excecao: o alerta nao pode esconder a falha que ele avisa.
"""
from __future__ import annotations

import json
import os
import urllib.request
from typing import Callable, Iterable, Mapping, Optional, Sequence

VAR_WEBHOOK = "ALERTA_WEBHOOK_URL"
NAO_CONFIGURADO, ENVIADO, FALHA_ENVIO = "NAO_CONFIGURADO", "ENVIADO", "FALHA_ENVIO"
MAX_MOTIVOS = 20
MAX_TEXTO = 3500


def mascarar(texto, segredos: Iterable[str] = ()) -> str:
    texto = str(texto)
    for segredo in sorted({s for s in segredos if s}, key=len, reverse=True):
        texto = texto.replace(segredo, "***")
    return texto


def montar_mensagem(veredito: str, motivos: Sequence[str] = (), segredos: Iterable[str] = (),
                    titulo: str = "SCDP viagens") -> str:
    segredos = tuple(segredos)
    linhas = [f"{titulo}: {veredito}"]
    linhas += [f"- {m}" for m in list(motivos)[:MAX_MOTIVOS]]
    if len(motivos) > MAX_MOTIVOS:
        linhas.append(f"- ... e mais {len(motivos) - MAX_MOTIVOS} motivos")
    return mascarar("\n".join(linhas), segredos)[:MAX_TEXTO]


def _segredos_do_ambiente(env: Mapping[str, str]) -> tuple:
    return tuple(v for v in (env.get(VAR_WEBHOOK), env.get("PORTAL_TRANSPARENCIA_API_KEY"), env.get("PGPASSWORD")) if v)


def enviar(mensagem: str, env: Optional[Mapping[str, str]] = None, abrir: Callable = urllib.request.urlopen,
           timeout: int = 10) -> str:
    env = os.environ if env is None else env
    url = (env.get(VAR_WEBHOOK) or "").strip()
    if not url:
        return NAO_CONFIGURADO
    if not url.startswith("https://"):
        return FALHA_ENVIO
    corpo = json.dumps({"text": mascarar(mensagem, _segredos_do_ambiente(env))}).encode("utf-8")
    pedido = urllib.request.Request(url, data=corpo, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with abrir(pedido, timeout=timeout) as resposta:
            return ENVIADO if 200 <= resposta.status < 300 else FALHA_ENVIO
    except Exception:
        return FALHA_ENVIO


def alertar(veredito: str, motivos: Sequence[str] = (), segredos: Iterable[str] = (),
            env: Optional[Mapping[str, str]] = None, abrir: Callable = urllib.request.urlopen,
            titulo: str = "SCDP viagens") -> str:
    env = os.environ if env is None else env
    if not (env.get(VAR_WEBHOOK) or "").strip():
        return NAO_CONFIGURADO
    mensagem = montar_mensagem(veredito, motivos, tuple(segredos) + _segredos_do_ambiente(env), titulo)
    return enviar(mensagem, env, abrir)


def callback_falha(ignorar_codigos: Sequence[int] = ()) -> Callable[[dict], str]:
    """on_failure_callback do Airflow; recebe o contexto da tarefa (nao importa o Airflow)."""
    def callback(contexto: dict) -> str:
        erro = str(contexto.get("exception") or "")
        if any(f"exit code {c}" in erro for c in ignorar_codigos):
            return NAO_CONFIGURADO
        ti = contexto.get("task_instance")
        onde = f"{getattr(ti, 'dag_id', '?')}.{getattr(ti, 'task_id', '?')}"
        return alertar("FALHA", [f"tarefa {onde} falhou", erro[:300]] if erro else [f"tarefa {onde} falhou"])
    return callback
