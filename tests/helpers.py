import copy
from collections import Counter


def viagem(vid, inicio, fim, total, passagem, diarias, outros=0.0, orgao="33000"):
    return {
        "id": vid,
        "viagem": {"pcdp": f"{vid:019d}", "numPcdp": f"{vid % 1000:06d}/26", "ano": 2026,
                   "urgenciaViagem": "Não", "motivo": "texto livre que não deve ir para a analítica"},
        "situacao": "Realizada", "tipoViagem": "Nacional",
        "beneficiario": {"nome": f"PESSOA {vid}", "cpfFormatado": "***.123.456-**"},
        "orgao": {"codigoSIAFI": orgao, "nome": "Ministério de Teste", "sigla": "MT",
                  "orgaoMaximo": {"sigla": "MT"}},
        "unidadeGestoraResponsavel": {"codigo": "330094", "nome": "UG TESTE"},
        "dataInicioAfastamento": inicio, "dataFimAfastamento": fim,
        "valorTotalViagem": total, "valorTotalPassagem": passagem, "valorTotalDiarias": diarias,
        "valorTotalTaxaAgenciamento": 0.0, "valorTotalRestituicao": 0.0,
        "valorTotalDevolucao": 0.0, "valorMulta": 0.0,
    }


class FakeExtrator:
    """Substitui o cliente da API. `resposta(ida, ret, n)` devolve a lista de registros ou uma Exception a levantar
    (`n` e o numero da chamada desta janela)."""

    def __init__(self, resposta):
        self.resposta = resposta
        self.chamadas = Counter()
        self.ordem = []

    def buscar(self, ida, ret):
        self.chamadas[(ida, ret)] += 1
        self.ordem.append((ida, ret))
        r = self.resposta(ida, ret, self.chamadas[(ida, ret)])
        if isinstance(r, Exception):
            raise r
        return copy.deepcopy(r), (1 if r else 0)
