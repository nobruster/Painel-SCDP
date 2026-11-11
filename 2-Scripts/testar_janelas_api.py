"""Consulta uma janela de /viagens e conta as viagens paginando ate `[]`.

Uso: python -I 2-Scripts/testar_janelas_api.py --ida-de 01/03/2026 --ida-ate 31/03/2026 --ret-de 01/03/2026 --ret-ate 31/03/2026
     python -I 2-Scripts/testar_janelas_api.py --casos 2-Scripts/casos_janela_ok.json
Saida: contagem e paginas (ou o erro 400); com --casos, uma linha por caso e exit 1 se algum divergir.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "3-Etl" / "dags"))

from scdp.config import Config  # noqa: E402
from scdp.extracao import MAX_PAGINAS, ClienteApi, ErroPermanente  # noqa: E402

PADRAO = object()


def contar(cliente: ClienteApi, ida_de, ida_ate, ret_de, ret_ate, orgao=PADRAO) -> Tuple[int, int]:
    """Devolve (viagens, paginas com dados). Parametro None nao e enviado; 400 sobe como ErroPermanente."""
    if orgao is PADRAO:
        orgao = cliente.cfg.orgao
    base = {"dataIdaDe": ida_de, "dataIdaAte": ida_ate, "dataRetornoDe": ret_de, "dataRetornoAte": ret_ate,
            "codigoOrgao": orgao}
    base = {k: v for k, v in base.items() if v is not None}
    total, ids_anteriores, pagina = 0, None, 1
    while True:
        if pagina > MAX_PAGINAS:
            raise RuntimeError(f"mais de {MAX_PAGINAS} paginas; a API parece nao estar paginando")
        dados = cliente._get({**base, "pagina": pagina})
        if not dados:
            return total, pagina - 1
        ids = [x.get("id") if isinstance(x, dict) else None for x in dados]
        if ids == ids_anteriores:
            raise RuntimeError(f"a API devolveu a pagina {pagina - 1} de novo; paginacao ignorada")
        ids_anteriores = ids
        total += len(dados)
        pagina += 1


def rodar_caso(cliente: ClienteApi, caso: dict) -> dict:
    """Executa um caso do JSON e compara com `esperado` ({resultado: ok|vazio|erro_400, contagem?})."""
    orgao = caso["orgao"] if "orgao" in caso else PADRAO
    esperado = caso["esperado"]
    try:
        qtd, paginas = contar(cliente, caso.get("ida_de"), caso.get("ida_ate"), caso.get("ret_de"),
                              caso.get("ret_ate"), orgao)
        resultado = "ok" if qtd else "vazio"
        contagem = qtd
    except ErroPermanente as e:
        if e.codigo != 400:
            raise
        resultado, contagem, paginas = "erro_400", None, 0
    aceitos = ("ok", "vazio") if esperado["resultado"] == "ok" else (esperado["resultado"],)
    certo = resultado in aceitos
    if certo and esperado.get("contagem") is not None and contagem != esperado["contagem"]:
        certo = False
    return {"nome": caso["nome"], "resultado": resultado, "contagem": contagem, "paginas": paginas, "certo": certo}


def rodar_casos(cliente: ClienteApi, casos: List[dict]) -> List[dict]:
    return [rodar_caso(cliente, c) for c in casos]


def _args(argv: Optional[List[str]]):
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--ida-de")
    p.add_argument("--ida-ate")
    p.add_argument("--ret-de")
    p.add_argument("--ret-ate")
    p.add_argument("--orgao", help="padrao: CODIGO_ORGAO do .env")
    p.add_argument("--casos", type=Path, help="JSON de casos esperados (casos_janela_ok.json / _erro.json)")
    return p.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    a = _args(argv)
    try:
        cfg = Config.do_ambiente()
        cliente = ClienteApi(cfg)
        if a.casos:
            casos = json.loads(a.casos.read_text(encoding="utf-8"))
            resultados = rodar_casos(cliente, casos)
            for r in resultados:
                print(f"{'OK ' if r['certo'] else 'FALHA'} {r['nome']}: {r['resultado']} contagem={r['contagem']} paginas={r['paginas']}")
            falhas = sum(not r["certo"] for r in resultados)
            print(f"{len(resultados) - falhas}/{len(resultados)} casos conferem")
            return 1 if falhas else 0
        orgao = a.orgao if a.orgao else PADRAO
        qtd, paginas = contar(cliente, a.ida_de, a.ida_ate, a.ret_de, a.ret_ate, orgao)
        print(f"viagens={qtd} paginas={paginas}")
        return 0
    except ErroPermanente as e:
        print(f"ERRO {e}")
        return 1
    except Exception as e:
        print(f"ERRO ({type(e).__name__}) {str(e)[:150]}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
