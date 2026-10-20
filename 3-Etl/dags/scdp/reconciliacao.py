"""Gate de reconciliacao: a staging, a intermediaria e a analitica contam a mesma historia e os valores fecham."""
from dataclasses import dataclass, field
from typing import List

OK, DIVERGENTE, NAO_MEDIDO = "OK", "DIVERGENTE", "NAO_MEDIDO"


@dataclass
class Resultado:
    veredito: str
    medidas: dict = field(default_factory=dict)
    motivos: List[str] = field(default_factory=list)


def _um(cur, sql: str):
    cur.execute(sql)
    return cur.fetchone()[0]


def reconciliar(cur) -> Resultado:
    m = {
        "stg": _um(cur, "SELECT count(*) FROM @STG@.stg_viagem"),
        "int": _um(cur, "SELECT count(*) FROM @INT@.int_viagem"),
        "fct": _um(cur, "SELECT count(*) FROM @ANA@.fct_viagem"),
        "obt": _um(cur, "SELECT count(*) FROM @ANA@.obt_viagem"),
    }
    # zero linhas lidas nao e zero divergencia: nada foi medido
    if m["int"] == 0:
        return Resultado(NAO_MEDIDO, m, ["int_viagem vazia: nada a reconciliar"])

    m["total_nulo"] = _um(cur, "SELECT count(*) FROM @INT@.int_viagem WHERE valor_total_viagem IS NULL")
    m["total_nao_fecha"] = _um(cur, """
        SELECT count(*) FROM @INT@.int_viagem
        WHERE valor_total_viagem IS NOT NULL
          AND valor_total_viagem <> coalesce(valor_passagem, 0) + coalesce(valor_diarias, 0)
              + coalesce(valor_taxa_agenciamento, 0) + coalesce(valor_restituicao, 0) + coalesce(valor_outros_gastos, 0)""")
    m["outros_gastos_negativo"] = _um(cur, "SELECT count(*) FROM @INT@.int_viagem WHERE valor_outros_gastos < 0")
    m["outros_gastos_positivo"] = _um(cur, "SELECT count(*) FROM @INT@.int_viagem WHERE valor_outros_gastos > 0")
    m["soma_total_int"] = str(_um(cur, "SELECT coalesce(sum(valor_total_viagem), 0) FROM @INT@.int_viagem"))
    m["soma_total_fct"] = str(_um(cur, "SELECT coalesce(sum(valor_total_viagem), 0) FROM @ANA@.fct_viagem"))

    motivos = []
    if m["stg"] != m["int"]:
        motivos.append(f"staging ({m['stg']}) e intermediaria ({m['int']}) com contagens diferentes")
    if m["fct"] != m["int"]:
        motivos.append(f"fct_viagem ({m['fct']}) e intermediaria ({m['int']}) com contagens diferentes")
    if m["obt"] != m["fct"]:
        motivos.append(f"obt_viagem ({m['obt']}) e fct_viagem ({m['fct']}) com contagens diferentes")
    if m["total_nao_fecha"]:
        motivos.append(f"{m['total_nao_fecha']} viagens com valor_total != passagem+diarias+taxa+restituicao+outros")
    if m["soma_total_int"] != m["soma_total_fct"]:
        motivos.append(f"soma do total difere: int {m['soma_total_int']} x fct {m['soma_total_fct']}")
    return Resultado(DIVERGENTE if motivos else OK, m, motivos)
