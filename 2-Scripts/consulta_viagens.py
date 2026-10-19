import os, time, requests

def load_env(path=".env"):
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

load_env(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))

URL = os.environ["PORTAL_TRANSPARENCIA_BASE_URL"] + "/viagens"
H = {"chave-api-dados": os.environ["PORTAL_TRANSPARENCIA_API_KEY"]}
params = {
    "dataIdaDe": "01/09/2026", "dataIdaAte": "30/09/2026",
    "dataRetornoDe": "01/09/2026", "dataRetornoAte": "30/09/2026",
    "codigoOrgao": os.environ["CODIGO_ORGAO"], "pagina": 1,
}
viagens = []
while True:
    r = requests.get(URL, headers=H, params=params, timeout=60)
    r.raise_for_status()
    dados = r.json()
    if not dados:
        break
    viagens += dados
    params["pagina"] += 1
    time.sleep(0.7)

print(f"Total de viagens: {len(viagens)}\n")
for v in viagens:
    p = v["viagem"]
    print(
        v["id"],
        v["dataInicioAfastamento"],
        v["dataFimAfastamento"],
        v["pessoaViajante"]["nome"] if "pessoaViajante" in v else v.get("beneficiario", {}).get("nome", ""),
        v.get("valorTotalViagem", ""),
        sep=" | ",
    )
