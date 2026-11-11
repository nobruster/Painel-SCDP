# Checklist final de entrega

Cada item tem o comando que o prova e o resultado esperado. Rodar da raiz do projeto, com `PYTHONIOENCODING=utf-8`. Marque so depois de ver o resultado esperado; este arquivo e o modelo, nao o registro de que foi feito.

| Feito | Item | Comando | Esperado |
|---|---|---|---|
| [ ] | Testes unitarios e de banco passam | `python -I -m pytest -q` (banco: definir `TEST_DATABASE_URL`) | 0 falhas |
| [ ] | Codigo compila | `python -m compileall -q 2-Scripts 3-Etl tests` | sem saida, exit 0 |
| [ ] | CI verde na branch/PR | `gh run list --branch <branch> --limit 1` | `completed success` (jobs `testes` e `segredos`) |
| [ ] | Reconciliacao entre camadas | `python -I 2-Scripts/verificar_reconciliacao.py` | `RECONCILIACAO=OK`, exit 0 |
| [ ] | Carga completa: todas as janelas OK | `python -I 2-Scripts/validar_carga_completa.py` | `CARGA=OK`, `sem_registro 0`, `fora_de_ok 0`, `qtd_diferente 0`, exit 0 |
| [ ] | Sem erros nem pendencias abertos | `SELECT count(*) FROM staging.vw_ctl_erros_abertos;` e `... vw_ctl_pendencias` | 0 e 0 |
| [ ] | Segredos fora do git (historico) | `gitleaks detect --source . --redact` (o CI roda o mesmo no job `segredos`) | `no leaks found` |
| [ ] | `.env` ignorado e nao rastreado | `git check-ignore .env` e `git ls-files .env` | primeiro imprime `.env`; segundo imprime nada |
| [ ] | `.env.example` sem valores | `grep -E "^[A-Z_]+=.+" .env.example` | nenhuma linha |
| [ ] | Actions fixadas por SHA | `python -I -m pytest -q tests/test_ci_actions_fixadas.py` | passa |
| [ ] | DAGs ativas (nao pausadas) | `airflow dags list` e `airflow dags details scdp_carga_diaria` (idem `scdp_carga_completa`) | as duas listadas, `is_paused: False`, agenda `0 2 * * *` e `30 3 1,11,21 * *` |
| [ ] | Ultima execucao de cada DAG verde | `airflow dags list-runs -d scdp_carga_diaria --no-backfill` (idem completa) | `success` |
| [ ] | Ultima carga CONCLUIDA | `SELECT * FROM staging.vw_ctl_execucoes ORDER BY 1 DESC LIMIT 1;` | status CONCLUIDA |
| [ ] | Alerta configurado | no worker: variavel `ALERTA_WEBHOOK_URL` definida (sem imprimir o valor) | definida; falha de teste chega no canal |
| [ ] | Papel de leitura do painel criado | `psql -f 3-Etl/dags/sql/papel_leitura.sql` aplicado; `\du` | papel existe, so SELECT na analitica |
| [ ] | Registro tardio exercitado | `SELECT count(*) FROM staging.vw_ctl_tardios;` (ver `validacao/registro-tardio.md`) | consulta roda; criterio no runbook |
| [ ] | Manuais e runbooks com conteudo | `wc -l 1-Documentos/MANUAL.md 1-Documentos/MANUAL-recuperacao.md 1-Documentos/validacao/*.md` | cada arquivo com dezenas de linhas, nao um modelo curto |
