"""Alerta: mensagem com veredito e motivos, segredos mascarados, sem configuracao nao acessa a rede."""
from types import SimpleNamespace

from scdp import alerta

URL = "https://hooks.exemplo.invalido/T0/B0/segredo-do-webhook"


class Resposta:
    def __init__(self, status=200):
        self.status = status

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def test_mensagem_traz_veredito_e_motivos():
    m = alerta.montar_mensagem("DIVERGENTE", ["janela 2025-01/2025-02 com erro", "qtd diferente"])
    assert "DIVERGENTE" in m and "janela 2025-01/2025-02 com erro" in m and "qtd diferente" in m


def test_mensagem_mascara_segredos():
    m = alerta.montar_mensagem("ERRO", ["falha com chave-de-teste"], segredos=["chave-de-teste"])
    assert "chave-de-teste" not in m and "***" in m


def test_sem_configuracao_nao_acessa_a_rede():
    def proibido(*a, **k):
        raise AssertionError("acessou a rede")

    assert alerta.alertar("FALHA", ["x"], env={}, abrir=proibido) == alerta.NAO_CONFIGURADO
    assert alerta.enviar("x", env={"ALERTA_WEBHOOK_URL": "  "}, abrir=proibido) == alerta.NAO_CONFIGURADO


def test_envio_posta_json_sem_o_segredo():
    chamadas = []

    def abrir(pedido, timeout):
        chamadas.append(pedido)
        return Resposta()

    env = {"ALERTA_WEBHOOK_URL": URL, "PORTAL_TRANSPARENCIA_API_KEY": "chave-de-teste"}
    assert alerta.alertar("FALHA", ["erro com chave-de-teste"], env=env, abrir=abrir) == alerta.ENVIADO
    pedido = chamadas[0]
    assert pedido.full_url == URL and pedido.get_method() == "POST"
    assert b"chave-de-teste" not in pedido.data and b"FALHA" in pedido.data


def test_falha_de_envio_nao_levanta():
    def abrir(pedido, timeout):
        raise OSError("sem rede")

    assert alerta.enviar("x", env={"ALERTA_WEBHOOK_URL": URL}, abrir=abrir) == alerta.FALHA_ENVIO
    assert alerta.enviar("x", env={"ALERTA_WEBHOOK_URL": "http://inseguro.invalido/x"}) == alerta.FALHA_ENVIO
    assert alerta.enviar("x", env={"ALERTA_WEBHOOK_URL": URL}, abrir=lambda p, timeout: Resposta(500)) == alerta.FALHA_ENVIO


def test_callback_ignora_codigo_ocupado_e_alerta_nos_demais(monkeypatch):
    enviados = []
    monkeypatch.setattr(alerta, "alertar", lambda v, m=(), *a, **k: enviados.append((v, list(m))) or alerta.ENVIADO)
    ti = SimpleNamespace(dag_id="scdp_carga_diaria", task_id="reconciliar")
    cb = alerta.callback_falha(ignorar_codigos=(3,))
    cb({"task_instance": ti, "exception": "Bash command failed. The command returned a non-zero exit code 3."})
    assert enviados == []
    cb({"task_instance": ti, "exception": "Bash command failed. The command returned a non-zero exit code 1."})
    assert enviados[0][0] == "FALHA" and "scdp_carga_diaria.reconciliar" in enviados[0][1][0]
