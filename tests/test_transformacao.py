from scdp import transformacao


def test_hash_nao_depende_da_ordem_das_chaves():
    a = {"id": 1, "valor": 10, "x": {"b": 1, "a": 2}}
    b = {"x": {"a": 2, "b": 1}, "valor": 10, "id": 1}
    assert transformacao.hash_registro(a) == transformacao.hash_registro(b)
    assert transformacao.hash_registro(a) != transformacao.hash_registro({**a, "valor": 11})


def test_remover_repetidos_mantem_o_ultimo_de_cada_id():
    a1, a2, b = {"id": 1, "v": "velho"}, {"id": 1, "v": "novo"}, {"id": 2}
    unicos, removidos = transformacao.remover_repetidos([a1, b, a2])
    assert removidos == 1
    assert sorted(x["id"] for x in unicos) == [1, 2]
    assert [x for x in unicos if x["id"] == 1][0]["v"] == "novo"


def test_classificar_separa_novos_alterados_e_iguais():
    iguais = {"id": 1, "v": 1}
    mudou = {"id": 2, "v": 2}
    novo = {"id": 3, "v": 3}
    existentes = {1: transformacao.hash_registro(iguais), 2: transformacao.hash_registro({"id": 2, "v": 0})}
    novos, alterados, hashes = transformacao.classificar([iguais, mudou, novo], existentes)
    assert novos == [novo]
    assert alterados == [mudou]
    assert set(hashes) == {1, 2, 3}
