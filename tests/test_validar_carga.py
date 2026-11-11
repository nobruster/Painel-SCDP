"""Gate de janelas: vazia = NAO_MEDIDO, divergencia = DIVERGENTE com a lista, tudo certo = OK."""
import datetime as dt
import importlib.util
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parent.parent / "2-Scripts" / "validar_carga_completa.py"
spec = importlib.util.spec_from_file_location("validar_carga_completa", SCRIPT)
validar = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validar)

D = dt.date
PLANEJADAS = [(D(2025, 1, 1), D(2025, 1, 1)), (D(2025, 1, 1), D(2025, 2, 1)), (D(2025, 2, 1), D(2025, 2, 1))]


class CursorFalso:
    def __init__(self, linhas):
        self.linhas = linhas

    def execute(self, sql, params=None):
        assert "ctl_janela" in sql and params == ("33000",)

    def fetchall(self):
        return self.linhas


def linha(ida, ret, status="OK", api=5, carregada=5):
    return (ida, ret, status, api, carregada)


def test_tabela_vazia_e_nao_medido():
    r = validar.verificar(CursorFalso([]), "33000", PLANEJADAS)
    assert r.veredito == "NAO_MEDIDO" and r.motivos


def test_tudo_certo_e_ok():
    r = validar.verificar(CursorFalso([linha(*j) for j in PLANEJADAS]), "33000", PLANEJADAS)
    assert r.veredito == "OK" and not r.motivos


def test_janela_com_erro_qtd_diferente_ou_ausente_e_divergente_com_a_lista():
    linhas = [linha(*PLANEJADAS[0], status="ERRO"), linha(*PLANEJADAS[1], api=5, carregada=4)]
    r = validar.verificar(CursorFalso(linhas), "33000", PLANEJADAS)
    texto = " | ".join(r.motivos)
    assert r.veredito == "DIVERGENTE"
    assert "2025-01/2025-01 (ERRO)" in texto
    assert "2025-01/2025-02 (api 5, carregada 4)" in texto
    assert "2025-02/2025-02" in texto and "sem registro" in texto


def test_qtd_api_nula_nao_passa():
    r = validar.verificar(CursorFalso([linha(*j, api=None, carregada=None) for j in PLANEJADAS]), "33000", PLANEJADAS)
    assert r.veredito == "DIVERGENTE"


def test_janela_fora_do_plano_nao_atrapalha():
    extra = linha(D(2030, 1, 1), D(2030, 1, 1), status="ERRO")
    r = validar.verificar(CursorFalso([linha(*j) for j in PLANEJADAS] + [extra]), "33000", PLANEJADAS)
    assert r.veredito == "OK"


def _inserir(banco, ida, ret, status="OK", api=3, carregada=3):
    banco.cur.execute(
        "INSERT INTO @STG@.ctl_janela (orgao, ida_mes, retorno_mes, status, qtd_api, qtd_carregada) "
        "VALUES (%s,%s,%s,%s,%s,%s)", (banco.cfg.orgao, ida, ret, status, api, carregada))


def test_banco_vazio_nao_medido(banco):
    assert validar.verificar(banco.cur, banco.cfg.orgao, PLANEJADAS).veredito == "NAO_MEDIDO"


def test_banco_ok_e_divergente(banco):
    for j in PLANEJADAS:
        _inserir(banco, *j)
    assert validar.verificar(banco.cur, banco.cfg.orgao, PLANEJADAS).veredito == "OK"
    banco.cur.execute("UPDATE @STG@.ctl_janela SET qtd_carregada = 2 WHERE ida_mes = %s AND retorno_mes = %s", PLANEJADAS[1])
    r = validar.verificar(banco.cur, banco.cfg.orgao, PLANEJADAS)
    assert r.veredito == "DIVERGENTE" and "2025-01/2025-02" in r.motivos[0]


def test_main_sem_configuracao_devolve_erro(monkeypatch, capsys):
    def falta(*a, **k):
        raise RuntimeError("sem config")

    monkeypatch.setattr(validar.Config, "do_ambiente", classmethod(falta))
    assert validar.main([]) == 1
    assert "CARGA=ERRO" in capsys.readouterr().out


def test_desde_invalido_sai_com_codigo_2():
    with pytest.raises(SystemExit) as e:
        validar.main(["--desde", "janeiro"])
    assert e.value.code == 2
