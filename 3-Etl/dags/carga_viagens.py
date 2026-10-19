import os, sys, time, json, hashlib, calendar, argparse, datetime as dt
import requests
import psycopg2
from psycopg2.extras import execute_values, Json

## bruno

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
MESES_RETORNO_APOS_IDA = 12
MESES_FUTUROS = 2
MESES_RECENTES = 3
LIMITE_DIA = 400
LIMITE_NOITE = 700
USO_DO_LIMITE = 0.5


def pausa():
    limite = LIMITE_NOITE if dt.datetime.now().hour < 6 else LIMITE_DIA
    time.sleep(60 / (limite * USO_DO_LIMITE))


def load_env(path):
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8") as f:
        for l in f:
            l = l.strip()
            if "=" in l and not l.startswith("#"):
                k, v = l.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip("\"'"))


load_env(os.path.join(ROOT, ".env"))
URL = os.environ["PORTAL_TRANSPARENCIA_BASE_URL"] + "/viagens"
H = {"chave-api-dados": os.environ["PORTAL_TRANSPARENCIA_API_KEY"]}
ORGAO = os.environ["CODIGO_ORGAO"]


def add_meses(d, n):
    m = d.month - 1 + n
    return dt.date(d.year + m // 12, m % 12 + 1, 1)


def faixa(d):
    ultimo = calendar.monthrange(d.year, d.month)[1]
    return d.strftime("01/%m/%Y"), f"{ultimo:02d}/{d.month:02d}/{d.year}"


def planejar(desde, hoje):
    ate_ida = add_meses(hoje.replace(day=1), MESES_FUTUROS)
    ida = desde
    while ida <= ate_ida:
        for k in range(MESES_RETORNO_APOS_IDA + 1):
            yield ida, add_meses(ida, k)
        ida = add_meses(ida, 1)


class ErroPermanente(Exception):
    pass


def get(params):
    for t in range(8):
        try:
            r = requests.get(URL, headers=H, params=params, timeout=90)
        except (requests.Timeout, requests.ConnectionError) as e:
            print(f"  rede {type(e).__name__}, tentativa {t + 1}", flush=True)
        else:
            if r.status_code == 200:
                pausa()
                return r.json()
            if r.status_code in (400, 401):
                raise ErroPermanente(f"{r.status_code} {r.text[:150]}")
            print(f"  status {r.status_code}, tentativa {t + 1}", flush=True)
            if r.status_code == 429:
                time.sleep(int(r.headers.get("Retry-After", 60)))
                continue
        time.sleep(4 * (t + 1))
    raise RuntimeError("API indisponivel apos 8 tentativas")


def buscar(ida, ret):
    ia, ib = faixa(ida)
    ra, rb = faixa(ret)
    out, p = [], 1
    while True:
        d = get(dict(dataIdaDe=ia, dataIdaAte=ib, dataRetornoDe=ra, dataRetornoAte=rb, codigoOrgao=ORGAO, pagina=p))
        if not d:
            return out, p - 1
        out += d
        p += 1


def hash_de(x):
    return hashlib.md5(json.dumps(x, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


def linha(x, ida, ret, h):
    return (x["id"], ida, ret, Json(x), h)


UPSERT = (
    "INSERT INTO @STG@.stg_viagem (id, janela_ida, janela_retorno, payload, hash_registro) VALUES %s "
    "ON CONFLICT (id) DO UPDATE SET janela_ida = EXCLUDED.janela_ida, janela_retorno = EXCLUDED.janela_retorno, "
    "payload = EXCLUDED.payload, hash_registro = EXCLUDED.hash_registro, atualizado_em = now()"
)

SILVER_UPSERT = """
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
        (b.payload->'viagem'->>'ano')::int AS ano, b.payload->>'situacao' AS situacao,
        b.payload->>'tipoViagem' AS tipo_viagem, b.payload->'viagem'->>'urgenciaViagem' AS urgencia_viagem,
        b.payload->'beneficiario'->>'nome' AS beneficiario_nome,
        b.payload->'beneficiario'->>'cpfFormatado' AS cpf_mascarado,
        b.payload->'orgao'->>'codigoSIAFI' AS orgao_siafi, b.payload->'orgao'->>'nome' AS orgao_nome,
        b.payload->'orgao'->>'sigla' AS orgao_sigla,
        b.payload->'orgao'->'orgaoMaximo'->>'sigla' AS orgao_maximo_sigla,
        b.payload->'unidadeGestoraResponsavel'->>'codigo' AS ug_codigo,
        b.payload->'unidadeGestoraResponsavel'->>'nome' AS ug_nome,
        (b.payload->>'dataInicioAfastamento')::date AS data_inicio, (b.payload->>'dataFimAfastamento')::date AS data_fim,
        (b.payload->>'valorTotalViagem')::numeric AS valor_total_viagem,
        (b.payload->>'valorTotalPassagem')::numeric AS valor_passagem,
        (b.payload->>'valorTotalDiarias')::numeric AS valor_diarias,
        (b.payload->>'valorTotalTaxaAgenciamento')::numeric AS valor_taxa_agenciamento,
        (b.payload->>'valorTotalRestituicao')::numeric AS valor_restituicao,
        (b.payload->>'valorTotalDevolucao')::numeric AS valor_devolucao,
        (b.payload->>'valorMulta')::numeric AS valor_multa,
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
SILVER_POR_IDS = SILVER_UPSERT.format(where="WHERE b.id = ANY(%s)")
SILVER_TUDO = SILVER_UPSERT.format(where="")


def precisa_ler(estado, ida, ret, hoje, modo):
    if modo == "completo" or estado is None or estado["status"] != "OK":
        return True
    limite = add_meses(hoje.replace(day=1), -MESES_RECENTES)
    return ida >= limite or ret >= limite


def processar(cur, conn, ida, ret, estado):
    cur.execute(
        """INSERT INTO @STG@.ctl_janela (orgao, ida_mes, retorno_mes, status, tentativas, inicio)
           VALUES (%s,%s,%s,'EXECUTANDO',1,now())
           ON CONFLICT (orgao, ida_mes, retorno_mes)
           DO UPDATE SET status='EXECUTANDO', tentativas=@STG@.ctl_janela.tentativas+1, inicio=now(), erro=NULL""",
        (ORGAO, ida, ret),
    )
    conn.commit()
    try:
        regs, paginas = buscar(ida, ret)
        anterior = estado["qtd_api"] if estado else None
        tentativas = 0
        while anterior and len(regs) < anterior and tentativas < 2:
            time.sleep(10)
            regs, paginas = buscar(ida, ret)
            tentativas += 1
        aviso = f"queda de {anterior} para {len(regs)} registros" if anterior and len(regs) < anterior else None

        ids = [x["id"] for x in regs]
        hashes = {x["id"]: hash_de(x) for x in regs}
        existentes = {}
        if ids:
            cur.execute("SELECT id, hash_registro FROM @STG@.stg_viagem WHERE id = ANY(%s)", (ids,))
            existentes = dict(cur.fetchall())
        novos = [x for x in regs if x["id"] not in existentes]
        alterados = [x for x in regs if x["id"] in existentes and existentes[x["id"]] != hashes[x["id"]]]
        grava = [linha(x, ida, ret, hashes[x["id"]]) for x in novos + alterados]
        if grava:
            execute_values(cur, UPSERT, grava, page_size=200)
            cur.execute(SILVER_POR_IDS, ([g[0] for g in grava],))

        carregadas = 0
        if ids:
            cur.execute("SELECT count(*) FROM @STG@.stg_viagem WHERE id = ANY(%s)", (ids,))
            carregadas = cur.fetchone()[0]
        ok = carregadas == len(ids)
        cur.execute(
            """UPDATE @STG@.ctl_janela SET status=%s, paginas_lidas=%s, qtd_api=%s, qtd_carregada=%s, qtd_novos=%s,
               qtd_alterados=%s, aviso=%s, erro=%s, fim=now() WHERE orgao=%s AND ida_mes=%s AND retorno_mes=%s""",
            ("OK" if ok else "ERRO", paginas, len(ids), carregadas, len(novos), len(alterados), aviso,
             None if ok else f"carregadas {carregadas} de {len(ids)}", ORGAO, ida, ret),
        )
        conn.commit()
        return ok, len(regs), len(novos), len(alterados), aviso
    except ErroPermanente:
        conn.rollback()
        raise
    except Exception as e:
        conn.rollback()
        cur.execute(
            "UPDATE @STG@.ctl_janela SET status='ERRO', erro=%s, fim=now() WHERE orgao=%s AND ida_mes=%s AND retorno_mes=%s",
            (str(e)[:500], ORGAO, ida, ret),
        )
        conn.commit()
        return False, 0, 0, 0, str(e)[:120]


S_STG = os.environ.get("SCHEMA_STG") or "staging"
S_INT = os.environ.get("SCHEMA_INT") or S_STG
S_ANA = os.environ.get("SCHEMA_ANA") or S_STG


class Cursor(psycopg2.extensions.cursor):
    def execute(self, query, vars=None):
        eh_bytes = isinstance(query, bytes)
        if eh_bytes:
            query = query.decode("utf-8")
        if isinstance(query, str):
            query = query.replace("@STG@", S_STG).replace("@INT@", S_INT).replace("@ANA@", S_ANA)
            if eh_bytes:
                query = query.encode("utf-8")
        return super().execute(query, vars)


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


def upsert(tabela, cols, select, chave):
    sets = ", ".join(f"{c} = EXCLUDED.{c}" for c in cols if c != chave)
    return (f"INSERT INTO {tabela} ({', '.join(cols)}) {select} "
            f"ON CONFLICT ({chave}) DO UPDATE SET {sets}, atualizado_em = now()")


def atualizar_analitica(cur, tudo=False):
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

        cur.execute(upsert("@ANA@.fct_viagem", FCT_COLS,
            f"""SELECT i.id, i.pcdp, i.num_pcdp, i.data_inicio, i.data_fim, i.orgao_siafi, i.ug_codigo,
                       {BENEF_KEY}, {PERFIL_KEY}, i.dias_afastamento, i.valor_total_viagem, i.valor_passagem,
                       i.valor_diarias, i.valor_taxa_agenciamento, i.valor_restituicao, i.valor_devolucao,
                       i.valor_multa, i.valor_outros_gastos {origem}""", "viagem_id"))

        cur.execute("INSERT INTO tmp_obt_ids SELECT id FROM tmp_viagem_ids")
        if orgaos_mudaram or ugs_mudaram:
            cur.execute("""INSERT INTO tmp_obt_ids SELECT viagem_id FROM @ANA@.fct_viagem
                           WHERE orgao_siafi = ANY(%s) OR ug_codigo = ANY(%s) ON CONFLICT DO NOTHING""",
                        (orgaos_mudaram, ugs_mudaram))
        cur.execute(upsert("@ANA@.obt_viagem", OBT_COLS,
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


def conectar():
    schema = os.environ.get("PGSCHEMA") or S_STG
    opcoes = f"-c search_path={schema}"
    if os.environ.get("DATABASE_URL"):
        return psycopg2.connect(os.environ["DATABASE_URL"], options=opcoes, cursor_factory=Cursor)
    faltando = [k for k in ("PGHOST", "PGDATABASE", "PGUSER", "PGPASSWORD") if not os.environ.get(k)]
    if faltando:
        raise SystemExit("Preencha no .env: " + ", ".join(faltando))
    return psycopg2.connect(
        host=os.environ["PGHOST"], port=os.environ.get("PGPORT") or 5432, dbname=os.environ["PGDATABASE"],
        user=os.environ["PGUSER"], password=os.environ["PGPASSWORD"],
        sslmode=os.environ.get("PGSSLMODE") or "prefer", options=opcoes, cursor_factory=Cursor,
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--desde", default="2025-01", help="mes inicial de ida (YYYY-MM)")
    ap.add_argument("--modo", choices=["diario", "completo"], default="diario",
                    help="diario: janelas dos últimos 3 meses + pendentes; completo: todas as janelas desde --desde")
    ap.add_argument("--reconstruir-silver", action="store_true", help="recria a intermediária e a analítica a partir de toda a staging, sem chamar a API")
    ap.add_argument("--dry-run", action="store_true", help="só consulta a API e conta, sem banco")
    a = ap.parse_args()
    desde = dt.datetime.strptime(a.desde, "%Y-%m").date()
    hoje = dt.date.today()
    janelas = list(planejar(desde, hoje))

    if a.dry_run:
        tot = 0
        for ida, ret in janelas:
            regs, _ = buscar(ida, ret)
            tot += len(regs)
            if regs:
                print(f"ida {ida:%Y-%m} -> ret {ret:%Y-%m}: {len(regs)}", flush=True)
        print("TOTAL", tot)
        return 0

    conn = conectar()
    cur = conn.cursor()
    cur.execute(open(os.path.join(HERE, "sql", "schema.sql"), encoding="utf-8").read())
    if a.reconstruir_silver:
        cur.execute(SILVER_TUDO)
        cur.execute("SELECT count(*) FROM @INT@.int_viagem")
        print("intermediária reconstruída:", cur.fetchone()[0], "registros")
        print("analítica reconstruída:", atualizar_analitica(cur, tudo=True), "viagens")
        conn.commit()
        return 0
    cur.execute("INSERT INTO @STG@.ctl_execucao (modo, janelas_total) VALUES (%s,%s) RETURNING id",
                (a.modo, len(janelas)))
    exec_id = cur.fetchone()[0]
    conn.commit()

    cur.execute("SELECT ida_mes, retorno_mes, status, qtd_api, fim FROM @STG@.ctl_janela WHERE orgao=%s", (ORGAO,))
    estados = {(r[0], r[1]): dict(status=r[2], qtd_api=r[3], fim=r[4]) for r in cur.fetchall()}

    lidas = erros = novos = alterados = tardios = 0
    limite_recente = add_meses(hoje.replace(day=1), -MESES_RECENTES)
    for ida, ret in janelas:
        est = estados.get((ida, ret))
        if not precisa_ler(est, ida, ret, hoje, a.modo):
            continue
        ok, qtd, n, alt, aviso = processar(cur, conn, ida, ret, est)
        lidas += 1
        novos += n
        alterados += alt
        erros += 0 if ok else 1
        atrasado = n > 0 and est is not None and est["status"] == "OK" and ida < limite_recente
        tardios += n if atrasado else 0
        if qtd or n or alt or aviso or not ok:
            print(f"ida {ida:%Y-%m} -> ret {ret:%Y-%m}: api={qtd} novos={n} alterados={alt}"
                  f"{' TARDIO' if atrasado else ''}{' AVISO ' + aviso if aviso else ''}{'' if ok else ' ERRO'}", flush=True)

    analiticas = atualizar_analitica(cur)
    conn.commit()
    print(f"analítica: {analiticas} viagens processadas")
    cur.execute("UPDATE @STG@.ctl_execucao SET fim=now(), janelas_lidas=%s, janelas_erro=%s, novos=%s, alterados=%s WHERE id=%s",
                (lidas, erros, novos, alterados, exec_id))
    conn.commit()
    cur.execute("SELECT count(*) FROM @STG@.ctl_janela WHERE orgao=%s AND status<>'OK'", (ORGAO,))
    pend = cur.fetchone()[0]
    print(f"janelas planejadas={len(janelas)} lidas={lidas} erro={erros} pendentes={pend} novos={novos} alterados={alterados} tardios={tardios}")
    return 1 if erros or pend else 0


if __name__ == "__main__":
    sys.exit(main())
