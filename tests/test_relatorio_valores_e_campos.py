import json
from decimal import Decimal

from api_simulada import carregar_script

script = carregar_script("relatorio_valores_e_campos")

PAYLOADS = [
    {"id": 1, "viagem": {"pcdp": "0001", "motivo": "x"}, "nis": None, "valorMulta": 0, "valorTotalViagem": 10.5,
     "tags": ["a", "b"], "vazia": []},
    json.dumps({"id": 2, "viagem": {"pcdp": "0002", "motivo": ""}, "nis": None, "valorMulta": 0,
                "valorTotalViagem": 5, "tags": [], "vazia": []}),
]


class CursorFalso:
    def __init__(self):
        self.consultas, self.linhas = [], []

    def execute(self, sql, params=None):
        self.consultas.append((sql, params))
        self.linhas = (
            [(3, 2, Decimal("1000.5"), Decimal("2000"), Decimal("3100.5")), (4, 1, Decimal("10"), Decimal("20"), Decimal("35"))]
            if "int_viagem WHERE" in sql and "stg_viagem" not in sql else [(p,) for p in PAYLOADS]
        )

    def fetchall(self):
        return self.linhas

    def fetchmany(self, n):
        lote, self.linhas = self.linhas[:n], self.linhas[n:]
        return lote

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


class ConexaoFalsa(CursorFalso):
    def __init__(self, cursor):
        self.c = cursor

    def cursor(self):
        return self.c


def test_formato_brl():
    assert script.brl(Decimal("1234567.5")) == "1.234.567,50"


def test_somas_por_mes_e_total():
    saida = []
    cur = CursorFalso()
    linhas = script.somas_por_mes(cur, "33000", 2026)
    assert cur.consultas[0][1] == ("33000", 2026)
    script.imprimir_valores(linhas, saida.append)
    assert any(l.startswith("  3") and "1.000,50" in l and "3.100,50" in l for l in saida)
    ano = next(l for l in saida if l.startswith("ano"))
    assert "3" in ano.split()[1] and "1.010,50" in ano and "3.135,50" in ano
    assert saida[-1] == "diarias + passagens: 3.030,50"


def test_preenchido():
    assert [script.preenchido(v) for v in (None, "", "  ", 0, 0.0, [], {}, "a", 1, 0.5, True, False)] == \
           [False, False, False, False, False, False, False, True, True, True, True, False]


def test_inventario_presente_e_preenchido():
    total, campos = script.inventario(PAYLOADS)
    assert total == 2
    assert campos["id"] == [2, 2]
    assert campos["viagem.motivo"] == [2, 1]
    assert campos["nis"] == [2, 0]
    assert campos["valorMulta"] == [2, 0]
    assert campos["tags[]"] == [1, 1] and campos["tags"] == [1, 0]
    assert campos["vazia"] == [2, 0]


def test_inventario_lista_de_objetos_conta_uma_vez_por_viagem():
    total, campos = script.inventario([{"a": [{"b": 1}, {"b": 2}]}])
    assert campos == {"a[].b": [1, 1]}


def test_main_completo(cfg, monkeypatch, capsys):
    cur = CursorFalso()
    monkeypatch.setattr(script.Config, "do_ambiente", classmethod(lambda c, *a: cfg))
    monkeypatch.setattr(script.carga, "conectar", lambda c: ConexaoFalsa(cur))
    assert script.main(["--ano", "2026"]) == 0
    saida = capsys.readouterr().out
    assert "orgao 33000, ano 2026" in saida and "diarias + passagens" in saida
    assert "viagem.pcdp" in saida and "sempre vazio" in saida
    assert cfg.chave_api not in saida


def test_main_so_valores_nao_le_payloads(cfg, monkeypatch, capsys):
    cur = CursorFalso()
    monkeypatch.setattr(script.Config, "do_ambiente", classmethod(lambda c, *a: cfg))
    monkeypatch.setattr(script.carga, "conectar", lambda c: ConexaoFalsa(cur))
    assert script.main(["--ano", "2026", "--orgao", "37202", "--so-valores"]) == 0
    assert len(cur.consultas) == 1 and cur.consultas[0][1] == ("37202", 2026)
    assert "campos da API" not in capsys.readouterr().out


def test_main_erro_sai_1(cfg, monkeypatch, capsys):
    monkeypatch.setattr(script.Config, "do_ambiente", classmethod(lambda c, *a: cfg))

    def falha(c):
        raise RuntimeError("sem conexao")

    monkeypatch.setattr(script.carga, "conectar", falha)
    assert script.main(["--ano", "2026"]) == 1
    assert "ERRO" in capsys.readouterr().out
