"""Transformacao: regras sobre os dados ja carregados (staging -> intermediaria -> analitica).

Os SQL usam os marcadores @STG@, @INT@ e @ANA@, trocados pelos schemas configurados (ver carga.criar_cursor).
"""
from __future__ import annotations

import hashlib
import json
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

INT_UPSERT = """
INSERT INTO @INT@.int_viagem (id, janela_ida, janela_retorno, pcdp, num_pcdp, ano, situacao, tipo_viagem, urgencia_viagem,
    beneficiario_nome, cpf_mascarado, orgao_siafi, orgao_nome, orgao_sigla, orgao_maximo_sigla, ug_codigo, ug_nome, data_inicio, data_fim,
    dias_afastamento, valor_total_viagem, valor_passagem, valor_diarias, valor_taxa_agenciamento, valor_restituicao,
    valor_devolucao, valor_multa, valor_outros_gastos, motivo, atualizado_em)
SELECT id, janela_ida, janela_retorno, pcdp, num_pcdp, ano, situacao, tipo_viagem, urgencia_viagem,
    beneficiario_nome, cpf_mascarado, orgao_siafi, orgao_nome, orgao_sigla, orgao_maximo_sigla, ug_codigo, ug_nome, data_inicio, data_fim,
    (data_fim - data_inicio) + 1, valor_total_viagem, valor_passagem, valor_diarias, valor_taxa_agenciamento,
    valor_restituicao, valor_devolucao, valor_multa,
    round(valor_total_viagem - coalesce(valor_passagem,0) - coalesce(valor_diarias,0)
          - coalesce(valor_taxa_agenciamento,0) - coalesce(valor_restituicao,0), 2),
    motivo, now()
FROM (
    SELECT b.id, b.janela_ida, b.janela_retorno,
        b.payload->'viagem'->>'pcdp' AS pcdp, b.payload->'viagem'->>'numPcdp' AS num_pcdp,
        @INT@.f_inteiro(b.payload->'viagem'->>'ano') AS ano, b.payload->>'situacao' AS situacao,
        b.payload->>'tipoViagem' AS tipo_viagem, b.payload->'viagem'->>'urgenciaViagem' AS urgencia_viagem,
        b.payload->'beneficiario'->>'nome' AS beneficiario_nome,
        b.payload->'beneficiario'->>'cpfFormatado' AS cpf_mascarado,
        b.payload->'orgao'->>'codigoSIAFI' AS orgao_siafi, b.payload->'orgao'->>'nome' AS orgao_nome,
        b.payload->'orgao'->>'sigla' AS orgao_sigla,
        b.payload->'orgao'->'orgaoMaximo'->>'sigla' AS orgao_maximo_sigla,
        b.payload->'unidadeGestoraResponsavel'->>'codigo' AS ug_codigo,
        b.payload->'unidadeGestoraResponsavel'->>'nome' AS ug_nome,
        @INT@.f_data(b.payload->>'dataInicioAfastamento') AS data_inicio, @INT@.f_data(b.payload->>'dataFimAfastamento') AS data_fim,
        @INT@.f_numero(b.payload->>'valorTotalViagem') AS valor_total_viagem,
        @INT@.f_numero(b.payload->>'valorTotalPassagem') AS valor_passagem,
        @INT@.f_numero(b.payload->>'valorTotalDiarias') AS valor_diarias,
        @INT@.f_numero(b.payload->>'valorTotalTaxaAgenciamento') AS valor_taxa_agenciamento,
        @INT@.f_numero(b.payload->>'valorTotalRestituicao') AS valor_restituicao,
        @INT@.f_numero(b.payload->>'valorTotalDevolucao') AS valor_devolucao,
        @INT@.f_numero(b.payload->>'valorMulta') AS valor_multa,
        b.payload->'viagem'->>'motivo' AS motivo
    FROM @STG@.stg_viagem b {where}
) s
ON CONFLICT (id) DO UPDATE SET
    janela_ida = EXCLUDED.janela_ida, janela_retorno = EXCLUDED.janela_retorno, pcdp = EXCLUDED.pcdp,
    num_pcdp = EXCLUDED.num_pcdp, ano = EXCLUDED.ano, situacao = EXCLUDED.situacao,
    tipo_viagem = EXCLUDED.tipo_viagem, urgencia_viagem = EXCLUDED.urgencia_viagem,
    beneficiario_nome = EXCLUDED.beneficiario_nome, cpf_mascarado = EXCLUDED.cpf_mascarado,
    orgao_siafi = EXCLUDED.orgao_siafi, orgao_nome = EXCLUDED.orgao_nome, orgao_sigla = EXCLUDED.orgao_sigla,
    orgao_maximo_sigla = EXCLUDED.orgao_maximo_sigla, ug_codigo = EXCLUDED.ug_codigo, ug_nome = EXCLUDED.ug_nome,
    data_inicio = EXCLUDED.data_inicio, data_fim = EXCLUDED.data_fim,
    dias_afastamento = EXCLUDED.dias_afastamento, valor_total_viagem = EXCLUDED.valor_total_viagem,
    valor_passagem = EXCLUDED.valor_passagem, valor_diarias = EXCLUDED.valor_diarias,
    valor_taxa_agenciamento = EXCLUDED.valor_taxa_agenciamento, valor_restituicao = EXCLUDED.valor_restituicao,
    valor_devolucao = EXCLUDED.valor_devolucao, valor_multa = EXCLUDED.valor_multa,
    valor_outros_gastos = EXCLUDED.valor_outros_gastos, motivo = EXCLUDED.motivo, atualizado_em = now()
"""

FCT_COLS = [
    "viagem_id", "pcdp", "num_pcdp", "data_inicio_key", "data_fim_key", "orgao_siafi", "ug_codigo",
    "beneficiario_key", "perfil_key", "dias_afastamento", "valor_total_viagem", "valor_passagem",
    "valor_diarias", "valor_taxa_agenciamento", "valor_restituicao", "valor_devolucao", "valor_multa",
    "valor_outros_gastos",
]
OBT_COLS = [
    "viagem_id", "pcdp", "num_pcdp", "data_inicio", "data_fim", "ano_inicio", "mes_inicio", "ano_mes_inicio",
    "trimestre_inicio", "orgao_siafi", "orgao_nome", "orgao_sigla", "orgao_maximo_sigla", "ug_codigo", "ug_nome",
    "beneficiario_nome", "cpf_mascarado", "situacao", "tipo_viagem", "urgencia_viagem", "dias_afastamento",
    "valor_total_viagem", "valor_passagem", "valor_diarias", "valor_taxa_agenciamento", "valor_restituicao",
    "valor_devolucao", "valor_multa", "valor_outros_gastos",
]
BENEF_KEY = "md5(coalesce(i.beneficiario_nome,'') || '|' || coalesce(i.cpf_mascarado,''))"
PERFIL_KEY = "md5(coalesce(i.situacao,'') || '|' || coalesce(i.tipo_viagem,'') || '|' || coalesce(i.urgencia_viagem,''))"


def hash_registro(registro: dict) -> str:
    """Hash estavel do JSON da API (independe da ordem das chaves), usado para detectar mudanca."""
    return hashlib.md5(json.dumps(registro, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


def remover_repetidos(registros: Sequence[dict]) -> Tuple[List[dict], int]:
    """A API pode repetir um id entre paginas; fica o ultimo. Devolve a lista unica e quantos foram descartados."""
    unicos = {x["id"]: x for x in registros}
    return list(unicos.values()), len(registros) - len(unicos)


def classificar(registros: Sequence[dict], hashes_existentes: Dict[int, str]) -> Tuple[List[dict], List[dict], Dict[int, str]]:
    """Separa o que e novo, o que mudou e o que ficou igual; devolve tambem o hash de cada registro."""
    hashes = {x["id"]: hash_registro(x) for x in registros}
    novos = [x for x in registros if x["id"] not in hashes_existentes]
    alterados = [x for x in registros if x["id"] in hashes_existentes and hashes_existentes[x["id"]] != hashes[x["id"]]]
    return novos, alterados, hashes


def atualizar_intermediaria(cur, ids: Optional[Iterable[int]] = None) -> None:
    """Staging -> intermediaria: tipa o JSON e calcula campos derivados. Sem `ids`, refaz tudo."""
    if ids is None:
        cur.execute(INT_UPSERT.format(where=""))
    else:
        cur.execute(INT_UPSERT.format(where="WHERE b.id = ANY(%s)"), (list(ids),))


def _upsert(tabela: str, cols: List[str], select: str, chave: str) -> str:
    sets = ", ".join(f"{c} = EXCLUDED.{c}" for c in cols if c != chave)
    return f"INSERT INTO {tabela} ({', '.join(cols)}) {select} ON CONFLICT ({chave}) DO UPDATE SET {sets}, atualizado_em = now()"


def atualizar_analitica(cur, tudo: bool = False) -> int:
    """Intermediaria -> analitica (dimensoes, fato e one big table), so com o que mudou desde a ultima marca d'agua."""
    cur.execute("SELECT marca FROM @STG@.ctl_camada WHERE camada = 'analitica'")
    r = cur.fetchone()
    marca = None if (tudo or r is None) else r[0]
    cur.execute("CREATE TEMP TABLE IF NOT EXISTS tmp_viagem_ids (id bigint PRIMARY KEY)")
    cur.execute("CREATE TEMP TABLE IF NOT EXISTS tmp_obt_ids (id bigint PRIMARY KEY)")
    cur.execute("TRUNCATE tmp_viagem_ids, tmp_obt_ids")
    cur.execute("INSERT INTO tmp_viagem_ids SELECT id FROM @INT@.int_viagem WHERE %s::timestamptz IS NULL OR atualizado_em >= %s",
                (marca, marca))
    cur.execute("SELECT count(*), max(i.atualizado_em) FROM @INT@.int_viagem i JOIN tmp_viagem_ids t ON t.id = i.id")
    qtd, nova_marca = cur.fetchone()
    if qtd:
        origem = "FROM @INT@.int_viagem i JOIN tmp_viagem_ids t ON t.id = i.id"
        cur.execute(f"""INSERT INTO @ANA@.dim_beneficiario (beneficiario_key, beneficiario_nome, cpf_mascarado)
                        SELECT DISTINCT {BENEF_KEY}, i.beneficiario_nome, i.cpf_mascarado {origem}
                        ON CONFLICT (beneficiario_key) DO NOTHING""")
        cur.execute(f"""INSERT INTO @ANA@.dim_perfil_viagem (perfil_key, situacao, tipo_viagem, urgencia_viagem)
                        SELECT DISTINCT {PERFIL_KEY}, i.situacao, i.tipo_viagem, i.urgencia_viagem {origem}
                        ON CONFLICT (perfil_key) DO NOTHING""")
        cur.execute(f"""INSERT INTO @ANA@.dim_orgao AS d (orgao_siafi, orgao_nome, orgao_sigla, orgao_maximo_sigla)
                        SELECT DISTINCT ON (i.orgao_siafi) i.orgao_siafi, i.orgao_nome, i.orgao_sigla, i.orgao_maximo_sigla
                        {origem} WHERE i.orgao_siafi IS NOT NULL ORDER BY i.orgao_siafi, i.atualizado_em DESC
                        ON CONFLICT (orgao_siafi) DO UPDATE SET orgao_nome = EXCLUDED.orgao_nome,
                          orgao_sigla = EXCLUDED.orgao_sigla, orgao_maximo_sigla = EXCLUDED.orgao_maximo_sigla,
                          atualizado_em = now()
                        WHERE (d.orgao_nome, d.orgao_sigla, d.orgao_maximo_sigla)
                              IS DISTINCT FROM (EXCLUDED.orgao_nome, EXCLUDED.orgao_sigla, EXCLUDED.orgao_maximo_sigla)
                        RETURNING d.orgao_siafi""")
        orgaos_mudaram = [x[0] for x in cur.fetchall()]
        cur.execute(f"""INSERT INTO @ANA@.dim_ug AS d (ug_codigo, ug_nome)
                        SELECT DISTINCT ON (i.ug_codigo) i.ug_codigo, i.ug_nome {origem}
                        WHERE i.ug_codigo IS NOT NULL ORDER BY i.ug_codigo, i.atualizado_em DESC
                        ON CONFLICT (ug_codigo) DO UPDATE SET ug_nome = EXCLUDED.ug_nome, atualizado_em = now()
                        WHERE d.ug_nome IS DISTINCT FROM EXCLUDED.ug_nome
                        RETURNING d.ug_codigo""")
        ugs_mudaram = [x[0] for x in cur.fetchall()]

        cur.execute(_upsert("@ANA@.fct_viagem", FCT_COLS,
            f"""SELECT i.id, i.pcdp, i.num_pcdp, i.data_inicio, i.data_fim, i.orgao_siafi, i.ug_codigo,
                       {BENEF_KEY}, {PERFIL_KEY}, i.dias_afastamento, i.valor_total_viagem, i.valor_passagem,
                       i.valor_diarias, i.valor_taxa_agenciamento, i.valor_restituicao, i.valor_devolucao,
                       i.valor_multa, i.valor_outros_gastos {origem}""", "viagem_id"))

        cur.execute("INSERT INTO tmp_obt_ids SELECT id FROM tmp_viagem_ids")
        if orgaos_mudaram or ugs_mudaram:
            cur.execute("""INSERT INTO tmp_obt_ids SELECT viagem_id FROM @ANA@.fct_viagem
                           WHERE orgao_siafi = ANY(%s) OR ug_codigo = ANY(%s) ON CONFLICT DO NOTHING""",
                        (orgaos_mudaram, ugs_mudaram))
        cur.execute(_upsert("@ANA@.obt_viagem", OBT_COLS,
            """SELECT f.viagem_id, f.pcdp, f.num_pcdp, f.data_inicio_key, f.data_fim_key, d.ano, d.mes, d.ano_mes,
                      d.trimestre, o.orgao_siafi, o.orgao_nome, o.orgao_sigla, o.orgao_maximo_sigla, u.ug_codigo,
                      u.ug_nome, b.beneficiario_nome, b.cpf_mascarado, p.situacao, p.tipo_viagem, p.urgencia_viagem,
                      f.dias_afastamento, f.valor_total_viagem, f.valor_passagem, f.valor_diarias,
                      f.valor_taxa_agenciamento, f.valor_restituicao, f.valor_devolucao, f.valor_multa,
                      f.valor_outros_gastos
               FROM @ANA@.fct_viagem f JOIN tmp_obt_ids t ON t.id = f.viagem_id
               LEFT JOIN @ANA@.dim_data d ON d.data_key = f.data_inicio_key
               LEFT JOIN @ANA@.dim_orgao o ON o.orgao_siafi = f.orgao_siafi
               LEFT JOIN @ANA@.dim_ug u ON u.ug_codigo = f.ug_codigo
               LEFT JOIN @ANA@.dim_beneficiario b ON b.beneficiario_key = f.beneficiario_key
               LEFT JOIN @ANA@.dim_perfil_viagem p ON p.perfil_key = f.perfil_key""", "viagem_id"))
    cur.execute("""INSERT INTO @STG@.ctl_camada (camada, marca, linhas) VALUES ('analitica', %s, %s)
                   ON CONFLICT (camada) DO UPDATE SET marca = coalesce(EXCLUDED.marca, @STG@.ctl_camada.marca),
                   linhas = EXCLUDED.linhas, atualizado_em = now()""", (nova_marca, qtd))
    return qtd
