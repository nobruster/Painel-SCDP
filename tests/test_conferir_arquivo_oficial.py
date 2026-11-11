import datetime as dt
from decimal import Decimal

import pytest

from api_simulada import carregar_script

script = carregar_script("conferir_arquivo_oficial")

CABECALHO = ('"Identificador do processo de viagem";"Número da Proposta (PCDP)";"Situação";"Viagem Urgente";'
             '"Justificativa Urgência Viagem";"Código do órgão superior";"Nome do órgão superior";'
             '"Código órgão solicitante";"Nome órgão solicitante";"CPF viajante";"Nome";"Cargo";"Função";'
             '"Descrição Função";"Período - Data de início";"Período - Data de fim";"Destinos";"Motivo";'
             '"Valor diárias";"Valor passagens";"Valor devolução";"Valor outros gastos"')


def linha(pcdp, orgao, inicio, motivo="Reunião de trabalho", diarias="100,50", pass_="200,00", dev="0,00",
          outros="10,00", nome="Fulano"):
    return (f'"{pcdp}";"001/26";"Realizada";"NÃO";"";"33000";"MPS";"{orgao}";"MPS";"***.111.222-**";"{nome}";"";"";"";'
            f'"{inicio}";"{inicio}";"Brasília";"{motivo}";"{diarias}";"{pass_}";"{dev}";"{outros}"')


def csv_oficial(tmp_path, linhas):
    caminho = tmp_path / "2026_Viagem.csv"
    caminho.write_bytes(("\r\n".join([CABECALHO] + linhas) + "\r\n").encode("latin-1"))
    return caminho


def registro(pcdp, mes, **kw):
    base = dict(situacao="Realizada", nome="Fulano", data_inicio=dt.date(2026, mes, 5), data_fim=dt.date(2026, mes, 5),
                valor_diarias=Decimal("100.50"), valor_passagem=Decimal("200.00"), valor_devolucao=Decimal("0.00"),
                valor_total=Decimal("310.50"), motivo="reuniaodetrabalho")
    base.update(kw)
    return base


def test_ler_arquivo_filtra_orgao_e_ano_e_trata_decimal(tmp_path):
    caminho = csv_oficial(tmp_path, [
        linha("0000000000000000001", "33000", "05/03/2026"),
        linha("0000000000000000002", "37202", "05/03/2026"),
        linha("0000000000000000003", "33000", "05/12/2025"),
    ])
    v = script.ler_arquivo(caminho, "33000", 2026)
    assert list(v) == ["0000000000000000001"]
    r = v["0000000000000000001"]
    assert r["valor_total"] == Decimal("310.50") and r["data_inicio"] == dt.date(2026, 3, 5)
    assert r["motivo"] == "reuniaodetrabalho"


def test_arquivo_sem_coluna_obrigatoria(tmp_path):
    caminho = tmp_path / "x.csv"
    caminho.write_bytes('"A";"B"\r\n"1";"2"\r\n'.encode("latin-1"))
    with pytest.raises(ValueError):
        script.ler_arquivo(caminho, "33000", 2026)


def test_comparar_tudo_igual():
    a = {"1": registro("1", 3), "2": registro("2", 4)}
    r = script.comparar(a, {k: dict(v) for k, v in a.items()})
    assert script.conferido(r) and r["iguais"] == 2 and sorted(r["meses"]) == [3, 4]


def test_comparar_acha_divergencias():
    arq = {"1": registro("1", 3), "2": registro("2", 3), "3": registro("3", 5)}
    ban = {"1": registro("1", 3, valor_diarias=Decimal("1.00")), "2": registro("2", 3), "4": registro("4", 5)}
    r = script.comparar(arq, ban)
    assert not script.conferido(r)
    assert r["so_arquivo"] == ["3"] and r["so_banco"] == ["4"]
    assert r["divergencias"] == {"valor_diarias": ["1"]}
    assert r["iguais"] == 1


def test_motivo_ignora_acento_e_pontuacao():
    assert script.so_alfanumerico("Reunião, de Trabalho!") == script.so_alfanumerico("Reuniao de Trabalho")


def test_mes_com_valor_diferente_reprova():
    arq = {"1": registro("1", 3)}
    ban = {"1": registro("1", 3, valor_total=Decimal("1.00"))}
    r = script.comparar(arq, ban)
    assert not script.mes_confere(r["meses"][3]) and not script.conferido(r)


class CursorFalso:
    def __init__(self, linhas):
        self.linhas, self.consultas = linhas, []

    def execute(self, sql, params=None):
        self.consultas.append((sql, params))

    def fetchall(self):
        return self.linhas

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


class ConexaoFalsa(CursorFalso):
    def __init__(self, cursor):
        self.cursor_ = cursor

    def cursor(self):
        return self.cursor_


def linha_banco(pcdp="0000000000000000001"):
    return (pcdp, "Realizada", "Fulano", dt.date(2026, 3, 5), dt.date(2026, 3, 5), Decimal("100.50"),
            Decimal("200.00"), Decimal("0.00"), Decimal("310.50"), "Reunião de trabalho")


def preparar(monkeypatch, cfg, linhas_banco):
    cursor = CursorFalso(linhas_banco)
    monkeypatch.setattr(script.Config, "do_ambiente", classmethod(lambda c, *a: cfg))
    monkeypatch.setattr(script.carga, "conectar", lambda c: ConexaoFalsa(cursor))
    return cursor


def test_main_confere_sai_0(cfg, monkeypatch, tmp_path, capsys):
    cursor = preparar(monkeypatch, cfg, [linha_banco()])
    caminho = csv_oficial(tmp_path, [linha("0000000000000000001", "33000", "05/03/2026")])
    assert script.main(["--ano", "2026", "--arquivo", str(caminho)]) == 0
    saida = capsys.readouterr().out
    assert "CONFERENCIA=OK" in saida and "1 de 1" in saida
    assert cursor.consultas[0][1] == ("33000", 2026)


def test_main_divergente_sai_1(cfg, monkeypatch, tmp_path, capsys):
    preparar(monkeypatch, cfg, [])
    caminho = csv_oficial(tmp_path, [linha("0000000000000000001", "33000", "05/03/2026")])
    assert script.main(["--ano", "2026", "--arquivo", str(caminho)]) == 1
    saida = capsys.readouterr().out
    assert "CONFERENCIA=DIVERGENTE" in saida and "so no arquivo: 1" in saida


def test_main_arquivo_inexistente(cfg, monkeypatch, tmp_path, capsys):
    preparar(monkeypatch, cfg, [])
    assert script.main(["--ano", "2026", "--arquivo", str(tmp_path / "nao.csv")]) == 1
    assert "CONFERENCIA=ERRO" in capsys.readouterr().out


def test_main_erro_de_banco_nao_vaza_segredo(cfg, monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(script.Config, "do_ambiente", classmethod(lambda c, *a: cfg))

    def falha(c):
        raise RuntimeError("sem conexao")

    monkeypatch.setattr(script.carga, "conectar", falha)
    caminho = csv_oficial(tmp_path, [linha("0000000000000000001", "33000", "05/03/2026")])
    assert script.main(["--ano", "2026", "--arquivo", str(caminho)]) == 1
    saida = capsys.readouterr().out
    assert "ERRO" in saida and cfg.chave_api not in saida
