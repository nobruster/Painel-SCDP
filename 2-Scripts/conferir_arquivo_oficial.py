"""Confere o banco (int_viagem) com o CSV oficial {ANO}_Viagem.csv do Portal, por mes e campo a campo.

Uso: python -I 2-Scripts/conferir_arquivo_oficial.py --ano 2025 [--arquivo caminho.csv] [--orgao 33000]
Padrao do arquivo: 1-Documentos/{ANO}_Viagem.csv. Exit 0 se tudo confere, 1 se houver divergencia ou erro.
Campos estritos: situacao, nome, datas, diarias, passagens, devolucao, total e motivo (so letras e numeros).
Divergencias ja documentadas (restituicao em outros gastos, CPF e numPcdp de sigilosas) nao entram.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import re
import sys
import unicodedata
from collections import defaultdict
from decimal import Decimal
from pathlib import Path
from typing import Dict, List, Optional

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "3-Etl" / "dags"))

from scdp import carga  # noqa: E402
from scdp.config import Config  # noqa: E402

COLUNAS = {
    "pcdp": "identificador do processo de viagem",
    "orgao": "codigo orgao solicitante",
    "situacao": "situacao",
    "nome": "nome",
    "inicio": "periodo - data de inicio",
    "fim": "periodo - data de fim",
    "motivo": "motivo",
    "diarias": "valor diarias",
    "passagens": "valor passagens",
    "devolucao": "valor devolucao",
    "outros": "valor outros gastos",
}
CAMPOS = ("situacao", "nome", "data_inicio", "data_fim", "valor_diarias", "valor_passagem", "valor_devolucao",
          "valor_total", "motivo")
SQL_BANCO = (
    "SELECT pcdp, situacao, beneficiario_nome, data_inicio, data_fim, valor_diarias, valor_passagem, "
    "valor_devolucao, valor_total_viagem, motivo FROM @INT@.int_viagem "
    "WHERE orgao_siafi = %s AND extract(year FROM data_inicio) = %s"
)
ZERO = Decimal("0")


def normalizar_cabecalho(txt: str) -> str:
    txt = unicodedata.normalize("NFKD", txt.strip().lstrip("﻿")).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", txt).lower()


def so_alfanumerico(txt) -> str:
    sem_acento = unicodedata.normalize("NFKD", str(txt or "")).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]", "", sem_acento.lower())


def decimal_br(txt) -> Decimal:
    txt = (txt or "").strip().replace(".", "").replace(",", ".")
    try:
        return Decimal(txt).quantize(Decimal("0.01"))
    except Exception:
        return ZERO


def data_br(txt) -> Optional[dt.date]:
    try:
        return dt.datetime.strptime((txt or "").strip(), "%d/%m/%Y").date()
    except ValueError:
        return None


def ler_arquivo(caminho: Path, orgao: str, ano: int) -> Dict[str, dict]:
    """Viagens do orgao solicitante com inicio no ano, por identificador (id repetido: vale a ultima linha)."""
    viagens: Dict[str, dict] = {}
    with caminho.open(encoding="latin-1", newline="") as f:
        leitor = csv.reader(f, delimiter=";", quotechar='"')
        cab = [normalizar_cabecalho(c) for c in next(leitor)]
        faltando = [c for c in COLUNAS.values() if c not in cab]
        if faltando:
            raise ValueError("colunas ausentes no arquivo: " + ", ".join(faltando))
        pos = {k: cab.index(v) for k, v in COLUNAS.items()}
        for linha in leitor:
            if len(linha) < len(cab) or linha[pos["orgao"]].strip() != orgao:
                continue
            inicio = data_br(linha[pos["inicio"]])
            if inicio is None or inicio.year != ano:
                continue
            diarias, passagens = decimal_br(linha[pos["diarias"]]), decimal_br(linha[pos["passagens"]])
            viagens[linha[pos["pcdp"]].strip()] = {
                "situacao": linha[pos["situacao"]].strip(),
                "nome": linha[pos["nome"]].strip(),
                "data_inicio": inicio,
                "data_fim": data_br(linha[pos["fim"]]),
                "valor_diarias": diarias,
                "valor_passagem": passagens,
                "valor_devolucao": decimal_br(linha[pos["devolucao"]]),
                "valor_total": diarias + passagens + decimal_br(linha[pos["outros"]]),
                "motivo": so_alfanumerico(linha[pos["motivo"]]),
            }
    return viagens


def ler_banco(cur, orgao: str, ano: int) -> Dict[str, dict]:
    cur.execute(SQL_BANCO, (orgao, ano))
    viagens = {}
    for pcdp, sit, nome, ini, fim, dia, pas, dev, tot, motivo in cur.fetchall():
        viagens[str(pcdp).strip()] = {
            "situacao": (sit or "").strip(), "nome": (nome or "").strip(), "data_inicio": ini, "data_fim": fim,
            "valor_diarias": Decimal(dia or 0), "valor_passagem": Decimal(pas or 0),
            "valor_devolucao": Decimal(dev or 0), "valor_total": Decimal(tot or 0), "motivo": so_alfanumerico(motivo),
        }
    return viagens


def comparar(arquivo: Dict[str, dict], banco: Dict[str, dict]) -> dict:
    meses = defaultdict(lambda: {"qtd_arquivo": 0, "qtd_banco": 0, "valor_arquivo": ZERO, "valor_banco": ZERO})
    for chave, origem in (("arquivo", arquivo), ("banco", banco)):
        for v in origem.values():
            m = meses[v["data_inicio"].month]
            m["qtd_" + chave] += 1
            m["valor_" + chave] += v["valor_total"]
    divergencias = defaultdict(list)
    for pcdp in sorted(arquivo.keys() & banco.keys()):
        for campo in CAMPOS:
            if arquivo[pcdp][campo] != banco[pcdp][campo]:
                divergencias[campo].append(pcdp)
    return {
        "meses": dict(sorted(meses.items())),
        "so_arquivo": sorted(arquivo.keys() - banco.keys()),
        "so_banco": sorted(banco.keys() - arquivo.keys()),
        "iguais": len(arquivo.keys() & banco.keys()) - len({p for ps in divergencias.values() for p in ps}),
        "divergencias": dict(divergencias),
    }


def mes_confere(m: dict) -> bool:
    return m["qtd_arquivo"] == m["qtd_banco"] and m["valor_arquivo"] == m["valor_banco"]


def conferido(r: dict) -> bool:
    return not (r["so_arquivo"] or r["so_banco"] or r["divergencias"]) and all(mes_confere(m) for m in r["meses"].values())


def imprimir(r: dict, log=print) -> None:
    ok = sum(mes_confere(m) for m in r["meses"].values())
    log(f"meses iguais em quantidade e valor: {ok} de {len(r['meses'])}")
    for mes, m in r["meses"].items():
        marca = "ok " if mes_confere(m) else "DIF"
        log(f"  {marca} {mes:02d}: arquivo {m['qtd_arquivo']} / {m['valor_arquivo']}  banco {m['qtd_banco']} / {m['valor_banco']}")
    log(f"so no arquivo: {len(r['so_arquivo'])}; so no banco: {len(r['so_banco'])}; viagens iguais em todos os campos: {r['iguais']}")
    for campo, ids in r["divergencias"].items():
        log(f"  campo {campo}: {len(ids)} diferentes (ex.: {', '.join(ids[:3])})")
    log("CONFERENCIA=" + ("OK" if conferido(r) else "DIVERGENTE"))


def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--ano", type=int, required=True)
    p.add_argument("--arquivo", type=Path)
    p.add_argument("--orgao", help="padrao: CODIGO_ORGAO do .env")
    a = p.parse_args(argv)
    try:
        cfg = Config.do_ambiente()
        orgao = a.orgao or cfg.orgao
        caminho = a.arquivo or RAIZ / "1-Documentos" / f"{a.ano}_Viagem.csv"
        if not caminho.exists():
            print(f"CONFERENCIA=ERRO (arquivo nao encontrado: {caminho.name})")
            return 1
        arquivo = ler_arquivo(caminho, orgao, a.ano)
        with carga.conectar(cfg) as conn, conn.cursor() as cur:
            banco = ler_banco(cur, orgao, a.ano)
        resultado = comparar(arquivo, banco)
    except Exception as e:
        print(f"CONFERENCIA=ERRO ({type(e).__name__}) {str(e)[:150]}")
        return 1
    print(f"orgao {orgao}, ano {a.ano}: {len(arquivo)} no arquivo, {len(banco)} no banco")
    imprimir(resultado)
    return 0 if conferido(resultado) else 1


if __name__ == "__main__":
    sys.exit(main())
