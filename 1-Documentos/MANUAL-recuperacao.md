# Manual de recuperacao de falhas

Para cada falha conhecida: sintoma, causa e acao. Regra geral: a carga e incremental e idempotente, entao repetir e seguro. Nunca apague dado da staging para "limpar" uma falha; o reprocessamento corrige sozinho.

Comece sempre por:

```
SELECT * FROM staging.vw_ctl_saude;
SELECT * FROM staging.vw_ctl_erros_abertos;
SELECT * FROM staging.vw_ctl_pendencias;
SELECT * FROM staging.vw_ctl_execucoes ORDER BY 1 DESC LIMIT 5;
```

## Codigos de saida do script

| Codigo | Significado | Acao |
|---|---|---|
| 0 | carga limpa | nada |
| 1 | sobrou erro aberto, pendencia, execucao ABORTADA ou falha inesperada | ver `vw_ctl_erros_abertos`, tratar a causa e rodar de novo |
| 2 | configuracao invalida (variavel ausente, schema invalido, URL sem https) | corrigir o `.env` ou as variaveis do worker; a mensagem diz qual |
| codigo 3 | outra execucao segura a trava (`CODIGO_OCUPADO`) | ver "Trava ocupada" abaixo |
| 143 | interrompida por sinal (SIGTERM, Ctrl+C) | ver "Execucao INTERROMPIDA" |

No Airflow, o codigo 3 da diaria vira "skipped" e nao alerta; os demais codigos diferentes de 0 falham a tarefa e disparam o alerta.

## Execucao INTERROMPIDA

- Sintoma: `vw_ctl_execucoes` mostra status INTERROMPIDA (saida 143) ou uma execucao sem fim.
- Causa: o processo recebeu SIGTERM/Ctrl+C, estourou o `execution_timeout` da tarefa ou o worker morreu. Em sinal, o script faz rollback e marca a execucao como INTERROMPIDA; se o processo foi morto sem aviso, a execucao fica sem fim e a proxima carga, ao obter a trava, a marca como interrompida.
- Acao: nada a limpar. Rode de novo o mesmo modo. Janelas que ficaram no meio voltam como pendentes e sao relidas; a staging e atualizada por hash, sem duplicar.

## 401 e 403 (fatais)

- Sintoma: log "ABORTADO", execucao ABORTADA, saida 1, alerta.
- Causa: chave `PORTAL_TRANSPARENCIA_API_KEY` ausente, invalida ou suspensa (uso acima do limite pode suspender o token).
- Acao: obter ou renovar a chave, atualizar o `.env` ou a variavel do worker (nunca imprimir a chave), conferir com `python -I 2-Scripts/consulta_viagens.py` e rodar a carga. Nao adianta tentar de novo antes de trocar a chave. 400 e 404 sao erro permanente da janela (registrado em `vw_ctl_erros_abertos`, sem retry automatico): revisar parametros e o codigo do orgao.

## 429 (limite de requisicoes)

- Sintoma: log "status 429, tentativa N".
- Causa: passou de 400 req/min (6:00 a 23:59) ou 700 req/min (0:00 a 5:59).
- Acao: normalmente nenhuma. O cliente espera o `Retry-After` do portal (60 s se ausente, no maximo 300 s) e tenta de novo; o ritmo normal ja usa 50% do limite. Se aparecer com frequencia, nao rode duas cargas ao mesmo tempo nem varreduras de `2-Scripts` junto com a DAG; baixe `USO_DO_LIMITE` se for preciso.

## 504 e outras falhas intermitentes

- Sintoma: "status 504, tentativa N", timeouts ou respostas que nao sao lista.
- Causa: instabilidade do servidor do Portal, frequente.
- Acao: nenhuma imediata. Cada requisicao tem ate 8 tentativas com espera crescente e a janela que ainda falhar entra em nova rodada (2 rodadas ao fim da execucao). Se a janela continuar com erro, ela fica em `vw_ctl_erros_abertos` e a proxima carga a repete; rode de novo mais tarde, de preferencia na madrugada.

## Trava ocupada (CODIGO_OCUPADO, codigo 3) e sessao orfa

- Sintoma: log "outra execucao da carga esta em andamento ... trava com pid ..."; saida 3.
- Causa: uma carga (ou `--reconstruir-silver`) segura a trava advisory `scdp:{stg}:{int}:{ana}`; pode ser legitima ou uma sessao orfa (processo morto cuja conexao ficou aberta no banco).
- Acao:
  1. Ler o dono no log (pid, usuario, estado, ha quanto tempo esta parada) ou em `pg_locks` com `locktype = 'advisory'` junto de `pg_stat_activity`.
  2. Se for uma carga viva, aguardar; nao force.
  3. Se a sessao esta `idle` ou parada ha muito tempo e nao existe processo correspondente, encerrar so essa sessao: `SELECT pg_terminate_backend(<pid>);` (confirme o pid antes). A trava e liberada com a conexao.
  4. Rodar a carga de novo.

## Janela pendente ou com erro

- Sintoma: linha em `vw_ctl_pendencias` (status diferente de OK) ou erro em `vw_ctl_erros_abertos`.
- Acao: rodar `--modo diario` (le as pendentes) ou `--modo completo`. A janela volta a OK e o erro sai da lista. Conferir com `python -I 2-Scripts/validar_carga_completa.py` (`CARGA=OK`).
- Se `qtd_api` ficar diferente de `qtd_carregada`, a janela e DIVERGENTE: rodar de novo `--modo completo --desde AAAA-MM` a partir do mes da janela; persistindo, abrir chamado com o dono da API (`perguntas-dono-da-api.md`).

## Como reprocessar

- Janelas com problema: `python -I 3-Etl/dags/carga_viagens.py --modo completo --desde AAAA-MM` (le todas as janelas com ida a partir do mes informado).
- Camadas derivadas erradas, staging correta: `python -I 3-Etl/dags/carga_viagens.py --reconstruir-silver` (refaz intermediaria e analitica sem chamar a API; tambem usa a trava).
- Depois de qualquer reprocessamento: `python -I 2-Scripts/verificar_reconciliacao.py` e `python -I 2-Scripts/validar_carga_completa.py`; ambos devem sair com 0.

## Reconciliacao DIVERGENTE

Contagens ou soma diferentes entre staging, intermediaria e analitica: rodar `--reconstruir-silver`; se persistir, ler os motivos impressos pelo script. `NAO_MEDIDO` significa tabela vazia, nao aprovacao.

## Erro de banco

Mensagens de erro do banco sao gravadas sem o valor ofensivo e sem segredos. "conexao com o banco perdida" aborta a execucao: confirmar o banco no ar e rodar de novo. "nao foi possivel aplicar o schema agora (tabelas em uso)" significa lock no DDL: tentar de novo quando a leitura (painel, consulta longa) terminar.
