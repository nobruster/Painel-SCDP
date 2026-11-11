# Manual de operacao

Guia unico para quem opera a carga das viagens do SCDP (Portal da Transparencia, orgao MPS, SIAFI 33000) no PostgreSQL. Falhas e recuperacao estao em `MANUAL-recuperacao.md`.

## Visao geral

API do Portal -> `staging` (JSON como recebido) -> `intermediaria` (tipada) -> `analitica` (fato, dimensoes e `obt_viagem`). Todas as cargas sao incrementais e idempotentes. A unidade de leitura e a janela: mes de ida x mes de retorno (0 a +12 meses), desde 2025-01. Eram 312 janelas em out/2026 e sao 325 em nov/2026 (cresce 13 por mes).

## Agenda (Airflow 2.10, America/Sao_Paulo)

| DAG | Quando | Tarefas |
|---|---|---|
| `scdp_carga_diaria` | todo dia, 02:00 | `carga_diaria` -> `reconciliar` |
| `scdp_carga_completa` | dias 1, 11 e 21, 03:30 | `carga_completa` -> `reconciliar` -> `validar_janelas` |

- A diaria sai como "skipped" (nao como falha) quando termina com o codigo 3, ou seja, outra carga segurava a trava.
- Cada tarefa roda o script como subprocesso: `"${PAINEL_SCDP_PYTHON}" -I "${PAINEL_SCDP_HOME}/3-Etl/dags/carga_viagens.py" ...`. As duas variaveis sao do worker; os padroes sao `/opt/airflow/venv/bin/python` e `/opt/repos/Painel-SCDP`.
- Falha de tarefa dispara o alerta (ver abaixo). `reconciliar` e `validar_janelas` nao tem retry.

## Modos da carga

Comando (rodar da raiz do projeto, `PYTHONIOENCODING=utf-8`):

```
python -I 3-Etl/dags/carga_viagens.py --modo diario
python -I 3-Etl/dags/carga_viagens.py --modo completo --desde 2025-01
```

- `--modo diario` (padrao): le as janelas com ida ou retorno nos ultimos 3 meses mais as pendentes (cerca de 156).
- `--modo completo`: le todas as janelas desde `--desde`.
- `--desde AAAA-MM`: primeiro mes de ida (padrao `2025-01`; aceita de 2011 ao ano seguinte).
- `--reconstruir-silver`: refaz a intermediaria e a analitica a partir de toda a staging, sem chamar a API. Use depois de mudar regra de transformacao ou para corrigir derivadas.
- `--dry-run`: so consulta a API e conta, sem tocar no banco.

Codigos de saida: 0 limpa; 1 sobrou erro, pendencia ou abortada; 2 configuracao invalida; 3 outra execucao em andamento (trava); 143 interrompida por sinal.

## Gates

Dois gates de leitura, ambos so consultam o banco e saem com 0 apenas em `OK`:

```
python -I 2-Scripts/verificar_reconciliacao.py
python -I 2-Scripts/validar_carga_completa.py [--desde AAAA-MM]
```

- `verificar_reconciliacao.py` imprime `RECONCILIACAO=OK|DIVERGENTE|NAO_MEDIDO|ERRO`. Confere que staging, intermediaria, `fct_viagem` e `obt_viagem` tem a mesma contagem, que o total da viagem fecha (passagem + diarias + taxa + restituicao + outros gastos) e que a soma do total e igual na intermediaria e na fato.
- `validar_carga_completa.py` imprime `CARGA=OK|DIVERGENTE|NAO_MEDIDO|ERRO`. Confere que toda janela planejada existe em `ctl_janela`, esta com status OK e tem `qtd_api = qtd_carregada`.
- `NAO_MEDIDO` significa que nao havia o que medir (tabela vazia), nunca e aprovacao. `ERRO` e falha ao medir (conexao, configuracao).
- Runbooks com evidencia: `validacao/carga-completa-real.md` e `validacao/registro-tardio.md`.

## Observabilidade (views no schema de staging)

Consulte com `SELECT * FROM staging.<view>` (ajuste o schema se `SCHEMA_STG` for outro).

| View | Para que serve |
|---|---|
| `vw_ctl_saude` | resumo: janelas, erros, `qtd_api` contra carregada, ultima execucao, marca da analitica |
| `vw_ctl_erros_abertos` | erros ainda abertos, com `horas_aberto`; sai da lista quando corrigido |
| `vw_ctl_pendencias` | janelas fora de OK |
| `vw_ctl_execucoes` | execucoes com duracao em minutos e status (CONCLUIDA, COM_ERROS, ABORTADA, INTERROMPIDA) |
| `vw_ctl_tardios` | viagens antigas publicadas com atraso (ver `validacao/registro-tardio.md`) |

Estado saudavel: `vw_ctl_erros_abertos` e `vw_ctl_pendencias` vazias, ultima execucao CONCLUIDA.

## Alerta

Falha de tarefa chama `scdp.alerta.callback_falha`, que envia uma mensagem de texto por webhook HTTPS para a URL em `ALERTA_WEBHOOK_URL` (variavel do worker, segredo). Sem a variavel, o alerta e ignorado (`NAO_CONFIGURADO`). O envio nunca derruba a tarefa, a URL nunca aparece em log e a chave da API e a senha do banco sao mascaradas na mensagem. A diaria nao alerta no codigo 3.

## Variaveis de ambiente

Modelo em `.env.example`; o `.env` nunca vai para o git e nunca deve ser impresso. Variaveis do worker do Airflow tem prioridade sobre o `.env`.

| Variavel | Uso |
|---|---|
| `PORTAL_TRANSPARENCIA_BASE_URL` | obrigatoria, precisa ser `https://` |
| `PORTAL_TRANSPARENCIA_API_KEY` | obrigatoria, vai no cabecalho `chave-api-dados` |
| `CODIGO_ORGAO` | obrigatoria, SIAFI de 5 digitos (`33000`); lista separada por virgula para varios orgaos |
| `DATABASE_URL` | conexao completa; tem prioridade sobre `PG*` |
| `PGHOST`, `PGPORT`, `PGDATABASE`, `PGUSER`, `PGPASSWORD`, `PGSSLMODE` | conexao ao PostgreSQL (use conexao direta, sem pooler em modo transaction, por causa da trava) |
| `SCHEMA_STG`, `SCHEMA_INT`, `SCHEMA_ANA` | schema de cada camada (padrao `staging`; INT e ANA seguem STG se vazios) |
| `ALERTA_WEBHOOK_URL` | webhook do alerta (opcional) |
| `PAINEL_SCDP_HOME`, `PAINEL_SCDP_PYTHON` | raiz do projeto e Python do worker, usados pelas DAGs |

Ritmo da API: 400 req/min das 6:00 as 23:59 e 700 req/min das 0:00 as 5:59; o script usa 50% do limite.

## Rotina

1. Diariamente: confirmar que `scdp_carga_diaria` terminou verde e que `vw_ctl_erros_abertos` esta vazia.
2. Nos dias 1, 11 e 21: confirmar `reconciliar` e `validar_janelas` verdes (`RECONCILIACAO=OK`, `CARGA=OK`).
3. Qualquer outro resultado: seguir `MANUAL-recuperacao.md`.
