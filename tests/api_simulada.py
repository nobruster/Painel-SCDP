"""API de viagens simulada (sem rede) com as regras de janela do CLAUDE.md, para os testes dos scripts de 2-Scripts."""
import datetime as dt
import importlib.util
import calendar
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
POR_PAGINA = 15


def carregar_script(nome: str):
    spec = importlib.util.spec_from_file_location(nome, RAIZ / "2-Scripts" / f"{nome}.py")
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


class Resposta:
    def __init__(self, status, corpo, headers=None):
        self.status_code = status
        self._corpo = corpo
        self.text = str(corpo)
        self.headers = headers or {}

    def json(self):
        return self._corpo


def _data(txt):
    return dt.datetime.strptime(txt, "%d/%m/%Y").date()


def _mais_um_mes(d):
    m = d.month % 12 + 1
    a = d.year + (1 if d.month == 12 else 0)
    return dt.date(a, m, min(d.day, calendar.monthrange(a, m)[1]))


class SessaoSimulada:
    """Regras: 4 datas e codigoOrgao obrigatorios; par com mais de 1 mes = 400; Ate < De, retorno antes da ida,
    retorno 7+ meses depois da ida ou orgao diferente de `orgao_valido` = []; senao `contagens` (padrao 20) viagens."""

    def __init__(self, contagens=None, orgao_valido="33000", padrao=20):
        self.headers = {}
        self.contagens = contagens or {}
        self.orgao_valido = orgao_valido
        self.padrao = padrao
        self.chamadas = []

    def get(self, url, params=None, timeout=None, allow_redirects=True):
        self.chamadas.append(dict(params))
        obrig = ("dataIdaDe", "dataIdaAte", "dataRetornoDe", "dataRetornoAte", "codigoOrgao")
        if any(k not in params for k in obrig):
            return Resposta(400, {"Erro na API": "Parametro obrigatorio ausente"})
        try:
            ida_de, ida_ate = _data(params["dataIdaDe"]), _data(params["dataIdaAte"])
            ret_de, ret_ate = _data(params["dataRetornoDe"]), _data(params["dataRetornoAte"])
        except ValueError:
            return Resposta(400, {"Erro na API": "Data invalida"})
        for de, ate in ((ida_de, ida_ate), (ret_de, ret_ate)):
            if ate > _mais_um_mes(de):
                return Resposta(400, {"Erro na API": "O período deve ser de no máximo 1 mês."})
        total = self.padrao
        vazio = (ida_ate < ida_de or ret_ate < ret_de or ret_ate < ida_de or params["codigoOrgao"] != self.orgao_valido
                 or ret_de > _mais_um_mes_n(ida_ate, 6))
        chave = (params["dataIdaDe"], params["dataIdaAte"], params["dataRetornoDe"], params["dataRetornoAte"])
        if vazio:
            total = 0
        elif chave in self.contagens:
            total = self.contagens[chave]
        pagina = int(params.get("pagina", 1))
        ini = (pagina - 1) * POR_PAGINA
        return Resposta(200, [{"id": i + 1} for i in range(ini, min(total, ini + POR_PAGINA))])


def _mais_um_mes_n(d, n):
    for _ in range(n):
        d = _mais_um_mes(d)
    return d
