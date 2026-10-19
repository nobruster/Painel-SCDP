import os, time, json, calendar, requests, collections as C

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SAIDAS = os.path.join(HERE, "saidas")
OUT = os.path.join(SAIDAS, "viagens_2026_completo.json")
MATRIZ = os.path.join(SAIDAS, "varredura_matriz.json")


def load_env(path):
    with open(path, encoding="utf-8") as f:
        for l in f:
            l = l.strip()
            if "=" in l and not l.startswith("#"):
                k, v = l.split("=", 1)
                os.environ[k.strip()] = v.strip().strip("\"'")


load_env(os.path.join(ROOT, ".env"))

URL = os.environ["PORTAL_TRANSPARENCIA_BASE_URL"] + "/viagens"
H = {"chave-api-dados": os.environ["PORTAL_TRANSPARENCIA_API_KEY"]}
ORGAO = os.environ["CODIGO_ORGAO"]
ANO = 2026
MESES_RETORNO_APOS_IDA = 12
PAUSA = 0.7


def mes(y, m):
    y += (m - 1) // 12
    m = (m - 1) % 12 + 1
    return f"01/{m:02d}/{y}", f"{calendar.monthrange(y, m)[1]:02d}/{m:02d}/{y}"


def get(params):
    for t in range(8):
        try:
            r = requests.get(URL, headers=H, params=params, timeout=90)
            if r.status_code == 200:
                time.sleep(PAUSA)
                return r.json()
            print(f"  status {r.status_code}, tentativa {t + 1}", flush=True)
        except (requests.Timeout, requests.ConnectionError) as e:
            print(f"  erro de rede {type(e).__name__}, tentativa {t + 1}", flush=True)
        time.sleep(4 * (t + 1))
    raise SystemExit(f"FALHA {params}")


def fetch(q):
    out, p = [], 1
    while True:
        d = get(dict(codigoOrgao=ORGAO, pagina=p, **q))
        if not d:
            return out
        out += d
        p += 1


def salvar(viagens, matriz):
    for path, obj in ((OUT, list(viagens.values())), (MATRIZ, matriz)):
        with open(path + ".tmp", "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=False, indent=1 if obj is matriz else None)
        os.replace(path + ".tmp", path)


viagens, matriz = {}, {}
if os.path.exists(MATRIZ) and os.path.exists(OUT) and os.environ.get("RETOMAR") == "1":
    matriz = json.load(open(MATRIZ, encoding="utf-8"))
    viagens = {x["id"]: x for x in json.load(open(OUT, encoding="utf-8"))}

for mi in range(1, 13):
    ia, ib = mes(ANO, mi)
    for mr in range(mi, mi + MESES_RETORNO_APOS_IDA + 1):
        ra, rb = mes(ANO, mr)
        chave = f"ida{mi:02d}->ret{ra[3:]}"
        if chave in matriz:
            continue
        res = fetch(dict(dataIdaDe=ia, dataIdaAte=ib, dataRetornoDe=ra, dataRetornoAte=rb))
        matriz[chave] = len(res)
        for x in res:
            viagens[x["id"]] = x
        print(f"{chave}: {len(res)}", flush=True)
    salvar(viagens, matriz)

por = C.Counter((x.get("dataInicioAfastamento") or "sem-data")[:7] for x in viagens.values())
print("TOTAL", len(viagens))
for k in sorted(por):
    print(k, por[k])
